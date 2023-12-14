ARG FROM=rockylinux
ARG VERSION=8

FROM ${FROM}:${VERSION}

ARG FROM
ARG VERSION

RUN dnf update -y
RUN dnf install -y epel-release
RUN dnf groupinstall -y "RPM Development Tools"
RUN dnf install -y gcc gcc-c++ \
    libtool libtool-ltdl \
    make cmake \
    git \
    wget \
    tree \
    pkgconfig \
    rpmdevtools \
    rpmlint \
    sudo \
    libwebp-devel.x86_64 \
    libc-client-devel \
    freetds \
    freetds-devel \
    libfbclient2.x86_64 \
    libfbclient2-devel.x86_64 \
    automake autoconf \
    yum-utils rpm-build && \
    yum clean all

RUN dnf install -y http://rpms.remirepo.net/enterprise/remi-release-8.rpm

RUN useradd builder -u 1000 -m -G users,wheel -d /srv/pkg && \
    echo "builder ALL=(ALL:ALL) NOPASSWD:ALL" >> /etc/sudoers && \
    echo "# macros"                      >  /srv/pkg/.rpmmacros && \
    echo "%_topdir    /srv/pkg/rpm"      >> /srv/pkg/.rpmmacros && \
    echo "%_sourcedir %{_topdir}"        >> /srv/pkg/.rpmmacros && \
    echo "%_builddir  %{_topdir}"        >> /srv/pkg/.rpmmacros && \
    echo "%_specdir   %{_topdir}"        >> /srv/pkg/.rpmmacros && \
    echo "%_rpmdir    %{_topdir}"        >> /srv/pkg/.rpmmacros && \
    echo "%_srcrpmdir %{_topdir}"        >> /srv/pkg/.rpmmacros && \
    mkdir /srv/pkg/rpm && \
    chown -R builder /srv/pkg
USER builder

ENV FLAVOR=rpmbuild
ENV OS=$FROM
ENV DIST=$VERSION

#CMD /srv/rpmbuild/pkg
