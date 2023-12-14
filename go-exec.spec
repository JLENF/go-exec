Name: go-exec
Version: 1.0.1
Release: 1%{?dist}
Summary: go-exec is a client for execute command by remote webservice
License: MIT
URL: http://goexec.app

BuildRequires: golang
Requires: glibc

%description
go-exec is a client for execute command by remote webservice.

%build
%gobuild go-exec.go

%install
%{__install} -D -m 0755 %{_builddir}/%{name} %{buildroot}/%{_bindir}/%{name}
%{__install} -D -m 0644 %{_sourcedir}/%{name}.service %{buildroot}/etc/systemd/system/%{name}.service

%post
systemctl daemon-reload
systemctl enable %{name}.service

%clean
rm -rf %{buildroot}

%files
%{_bindir}/%{name}
/etc/systemd/system/%{name}.service