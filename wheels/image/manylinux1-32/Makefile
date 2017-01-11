TAG		:= starforge/manylinux1-32:latest

image-id: .dockerignore starforge.tar.gz
	docker build -t $(TAG) .
	docker images -q $(TAG) >$@

.dockerignore:
	echo 'Makefile' >$@

starforge.tar.gz:
	rm -rf ../../../build ../../../dist
	cd ../../../ && python setup.py sdist
	cp ../../../dist/starforge-*.tar.gz starforge.tar.gz
clean:
	rm -f .dockerignore image-id starforge.tar.gz
