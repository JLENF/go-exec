docker build -t localbuild/rocky:8 .
docker container run --rm --name buildrocky -it localbuild/rocky:8 /bin/bash

dnf install rpmdevtools wget curl vim golang nc lftp -y
rpmdev-setuptree
vim /root/rpmbuild/SPECS/go-exec.spec
vim /root/rpmbuild/BUILD/go-exec.go
vim /root/rpmbuild/SOURCES/go-exec.service
#cp go-exec.go /root/rpmbuild/BUILD/
cd /root/rpmbuild
rpmbuild -ba SPECS/go-exec.spec
