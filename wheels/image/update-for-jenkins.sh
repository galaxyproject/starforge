#!/bin/bash
#
# Script to run on mjolnir0 (Galaxy Jenkins Starforge build host) to update wheel build images
#
set -e

macos_snap_root='/btrfs/snapshots'
macos_snap_source='@postxcode-clean'
macos_snap_users='jenkins nate dannon'
macos_snap_name='@starforge'
macos_user_snap_dir='snapshots'
macos_ssh_port='2222'
macos_ssh_identity_file="$HOME/.ssh/id_rsa_osx_wheel_10_6"

function print_usage() {
    echo "usage: $(basename $0) [-glm]"
    echo '  -g: Append git short rev to version (automatic if version ends with `.dev*`)'
    echo '  -l: Build manylinux1 Docker images'
    echo '  -m: Build macOS QEMU images'
}

function get_tag() {
    image="$1"
    image_id="$(docker images -q ${image})"
    [ -n "${image_id}" ] && docker inspect "${image_id}" | jq '.[0].RepoTags[]' | tr -d '"' | grep -v ':latest$' || true
}

function get_version() {
    image="$1"
    docker run --rm ${image} /opt/wheelenv/bin/python -c 'import starforge; print(starforge.__version__)'
}

function check_commands() {
    r=0
    while [ -n "$1" ]; do
        if ! command -V $1; then
            echo "ERROR: missing required command on \$PATH: $1"
            r=1
        fi
    done
    return $r
}

function remove_new_images() {
    echo "$1, removing any images created thus far..."
    for image in "${new_images[@]}"; do
        echo "Removing image: ${image}"
        docker rmi ${image}
    done
}

linux=0
macos=0
shortrev=0
cmds=(uuidgen)
while getopts "lmg" opt; do
    case "$opt" in
        l)
            linux=1
            cmds+=(jq)
            ;;
        m)
            macos=1
            cmds+=(ansible-playbook)
            ;;
        g)
            shortrev=1
            ;;
        \?|h)
            print_usage
            exit 2
            ;;
    esac
done

if [ $linux -eq 0 -a $macos -eq 0 ]; then
    # not an error but might want to print usage as a hint
    print_usage
    exit 0
fi

# Ensure required commands exist
fail=0
for cmd in "${cmds[@]}"; do
    if ! command -V $cmd; then
        echo "ERROR: Missing required command on \$PATH: $cmd"
        fail=1
    fi
done
[ $fail -ne 0 ] && exit $fail

dir="$(readlink -f $(dirname $0))"

# Build source distribution
cd "${dir}/../.."

if [ -d 'dist' ]; then
    echo 'Removing build/ and dist/'
    rm -rf build dist
fi

echo 'Creating source distribution'
python setup.py sdist
tarball="$(echo dist/starforge-*.tar.gz)"
new_ver="${tarball##dist/starforge-}"
new_ver="${new_ver%%.tar.gz}"
echo "New Starforge (PEP 440 compliant) version is: $new_ver"

last=${new_ver##*.}
if [ $shortrev -ne 0 -o "${last:0:3}" == "dev" ]; then
    shortrev="$(git rev-parse --short HEAD)"
    new_ver+="-${shortrev}"
    echo "Adding git shortrev '${shortrev}' to version, version is: $new_ver"
fi

tmp_tag="$(uuidgen)" || { "Failed to generate UUID for temporary build tag"; exit 1; }

if [ $linux -eq 1 ]; then

    failed=()
    bases=()
    versions=()

    # docker images that should be removed upon failure
    new_images=()

    cd "${dir}"

    for base in 'starforge/manylinux1' 'starforge/manylinux1-32'; do
        if docker inspect --type=image ${base}:${new_ver} >/dev/null 2>&1; then
            echo "Image exists: '${base}:${new_ver}', skipped"
        elif ! docker inspect --type=image ${base}:latest >/dev/null 2>&1; then
            echo "Image '${base}:latest' does not exist, will create"
        else
            tag="$(get_tag ${base}:latest)"
            if [ -n "$tag" ]; then
                echo "Image '${base}:latest' has additional tag '${tag}', 'latest' tag is safe to overwrite"
            else
                ver="$(get_version ${base}:latest)"
                if [ -z "$ver" ]; then
                    echo "ERROR: Failed to determine ${base}:latest version, cannot create image archival tag"
                    failed+=("${base}:latest")
                elif $(docker inspect --type=image ${base}:${ver} >/dev/null 2>&1); then
                    echo "ERROR: Image already exists: ${base}:${ver}"
                    failed+=("${base}:latest")
                else
                    bases+=("$base")
                    versions+=("$ver")
                fi
            fi
        fi
    done

    [ ${#failed[@]} -ne 0 ] && { echo "Cannot automatically add archival tags to old image(s), please tag them manually: ${failed[*]}"; exit 1; }

    for (( i=0; i < ${#bases[@]}; i++ )); do
        image_id="$(docker images -q ${bases[$i]}:latest)"
        docker tag ${bases[$i]}:latest ${bases[$i]}:${versions[$i]}
        echo "Tagged '${bases[$i]}:latest' (image id: $image_id) as '${bases[$i]}:${versions[$i]}'"
    done

    for base in 'starforge/manylinux1' 'starforge/manylinux1-32'; do
        img_dir="${base##starforge/}"
        echo "Building ${base}:${new_ver}-${tmp_tag}"
        cd $img_dir &&
        make clean &&
        echo 'Makefile' > .dockerignore &&
        cp ../../../${tarball} starforge.tar.gz &&
        docker build -t ${base}:${new_ver}-${tmp_tag} . || { remove_new_images "Failed to build ${base}"; exit 1; }
        new_image="$(docker images -q ${base}:${new_ver}-${tmp_tag})" || { remove_new_images "Failed to get image ID for ${base}:${new_ver}-${tmp_tag}"; exit 1; }
        new_images+=("${new_image}")
        echo "New image for ${base} is ${new_image}"
        for tag in "${new_ver}" 'latest'; do
            echo "Tagging image ${new_image} with ${base}:${tag}"
            docker tag -f "${new_image}" "${base}:${tag}" || { remove_new_images "Failed to tag ${new_image} with tag ${base}:${tag}"; exit 1; }
        done
        echo "Removing temporary tag ${base}:${new_ver}-${tmp_tag}"
        docker rmi ${base}:${new_ver}-${tmp_tag}
        cd ..
    done

fi

if [ $macos -eq 1 ]; then

    cd "$dir"

    src_snap_path="${macos_snap_root}/${macos_snap_source}"
    new_snap_path="${macos_snap_root}/${macos_snap_name}-${new_ver}"
    tmp_snap_path="${new_snap_path}-${tmp_tag}"
    if [ -d "${new_snap_path}" ]; then
        echo "Image exists: '${new_snap_path}', skipped"
    elif [ ! -d "${src_snap_path}" ]; then
        echo "ERROR: Source snapshot '${src_snap_path}' does not exist"
        exit 1
    else
        rm -f starforge.tar.gz
        cp ../../${tarball} starforge.tar.gz
        echo "Snapshotting ${src_snap_path} to ${tmp_snap_path}"
        sudo btrfs subvolume snapshot ${src_snap_path} ${tmp_snap_path}
        echo "Launching KVM/QEMU image ${tmp_snap_path}"
        sudo bash -c "cd ${tmp_snap_path}; ./run --daemon -p ${macos_ssh_port}"
        echo "Waiting for guest"
        count=0
        while ! ssh -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no -o ConnectTimeout=5 -p ${macos_ssh_port} -i ${macos_ssh_identity_file} root@localhost /usr/bin/true; do
            (( ++count ))
            if [ $count -ge 20 ]; then
                echo "Giving up"
                sudo pkill -u root -f qemu-system-x86_64  # yowza!
                sleep 5
                sudo pkill -9 -u root -f qemu-system-x86_64
                exit 1
            fi
            echo "Connect attempt ${count} failed, sleeping..."
            sleep 5
        done
        echo "Running Playbook"
        ansible-playbook -i localhost, -e "ansible_ssh_port=${macos_ssh_port}" -e "ansible_ssh_private_key_file=${macos_ssh_identity_file}" -e "ssh_args='-o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no'" osx-playbook.yml
        echo "Shutting down"
        ssh -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no -p ${macos_ssh_port} -i ${macos_ssh_identity_file} root@localhost shutdown -h now || true  # returns 255
        count=0
        while pgrep -u root -f qemu-system-x86_64; do
            (( ++count ))
            if [ $count -ge 10 ]; then
                echo "Giving up"
                sudo pkill -u root -f qemu-system-x86_64
                sleep 5
                sudo pkill -9 -u root -f qemu-system-x86_64
                exit 1
            fi
            echo "Waiting for guest shutdown..."
            sleep 5
        done
        echo "Creating RO snapshot"
        sudo btrfs subvolume snapshot -r ${tmp_snap_path} ${new_snap_path}
        echo "Removing RW snapshot"
        sudo btrfs subvolume delete ${tmp_snap_path}
        for user in ${macos_snap_users}; do
            echo "Snapshotting for $user"
            sudo bash -c "cd ${new_snap_path}; ./snap_for $user"
        done
    fi

fi
