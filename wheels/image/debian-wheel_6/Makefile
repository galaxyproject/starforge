TAG		:= starforge/debian-wheel:6
WHEEL_VERSION	:= 3f496bdf2708
PIP_VERSION	:= ac76f866c181dc75fb9f5ac3cd5575b6bc32a3c2


image-id: .dockerignore buildpy.sh
	docker build -t $(TAG) .
	docker images -q $(TAG) >$@

.dockerignore:
	echo 'Makefile' >$@

buildpy.sh: ../buildpy.sh.in
	sed -e 's#WHEEL_VERSION#$(WHEEL_VERSION)#' \
		-e 's#PIP_VERSION#$(PIP_VERSION)#' \
		../buildpy.sh.in >$@

clean:
	rm -f .dockerignore image-id buildpy.sh
