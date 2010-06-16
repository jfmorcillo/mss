%define name mss
%define version 2.0dev
%define release 1
%global username mss
%global groupname mss

%if %mdkversion < 200610
%define py_puresitedir %{_prefix}/lib/python%{pyver}/site-packages/
%endif

Summary: Mandriva Server Setup
Name: %{name}
Version: %{version}
%define subrel 1
Release: %mkrel %{release}
Source0: %{name}-%{version}.tar.gz
Source1: %{name}.desktop
Source2: %{name}.png
License: GPL
Group: System/Servers
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-buildroot
Prefix: %{_prefix}
BuildArch: noarch
Vendor: Mandriva
Packager: Jean-Philippe Braun <jpbraun@mandriva.com>
BuildRequires: python-devel

%description
MSS aims to help system administrators to setup software quickly. (srpm)

%package -n	mss-agents
Summary: Mandriva Server Setup
Group: System/Servers
Requires(pre): shadow-utils
Requires(pre): initscripts
Requires(preun): initscripts
Requires: python
Requires: python-django >= 1.0.4
Requires: python-IPy >= 0.62
Requires: openssl

%description -n	mss-agents
XML-RPC server and web interface

%package -n	mss-modules-mes5
Summary: Mandriva Server Setup modules for MES5
Group: System/Servers
Requires: python
Requires: mss-agents

%description -n	mss-modules-mes5
MES5 Modules for MSS


%prep
%setup -q -n %{name}-%{version}

%build
python setup.py build

%pre -n mss-agents
# Add mss user
getent group %groupname >/dev/null || groupadd -r %groupname
getent passwd %username >/dev/null || \
useradd -r -g %username -d %{_sharedstatedir}/mss -s /sbin/nologin \
-c "User for Mandriva Server Setup" %username
exit 0

%preun -n mss-agents
[ -f /var/run/mss-agent.pid ] && /sbin/service mss-agent stop
[ -f /var/run/mss-www.pid ] && /sbin/service mss-www stop
# package uninstallation
if [ $1 -eq 0 ]; then
    %_preun_service mss-agent
    %_preun_service mss-www
fi
exit 0

%install
python setup.py install --single-version-externally-managed --root=%{buildroot}

install -d %{buildroot}%{_initrddir}
install -d %{buildroot}%{_sbindir}
install -d %{buildroot}%{_sharedstatedir}/mss/
install -d %{buildroot}%{_logdir}/mss/
install -d %{buildroot}%{_sysconfdir}/mss/ssl/

install -d %{buildroot}%{_datadir}/mdk/desktop/server/
install -d %{buildroot}%{_datadir}/applications/
install -d %{buildroot}%{_datadir}/pixmaps/

install -m0755 bin/agent/mss-agent.init %{buildroot}%{_initrddir}/mss-agent
install -m0755 bin/agent/mss-agent.py %{buildroot}%{_sbindir}/mss-agent.py
install -m0755 bin/www/mss-www.init %{buildroot}%{_initrddir}/mss-www

install -m0644 %{SOURCE1} %{buildroot}%{_datadir}/mdk/desktop/server/%{name}.desktop
install -m0644 %{SOURCE1} %{buildroot}%{_datadir}/applications/%{name}.desktop
install -m0644 %{SOURCE2} %{buildroot}%{_datadir}/pixmaps/%{name}.png

cat > README.urpmi <<EOF
You can access Mandriva Server Setup at https://127.0.0.1:8000/
EOF

%post -n mss-agents
# Generate SSL certs
if [ "$1" = "1" ]; then 
    umask 077 
    if [ ! -f %{_sysconfdir}/mss/ssl/localhost.key ]; then
        %{_bindir}/openssl genrsa -rand /proc/apm:/proc/cpuinfo:/proc/dma:/proc/filesystems:/proc/interrupts:/proc/ioports:/proc/pci:/proc/rtc:/proc/uptime 1024 > %{_sysconfdir}/mss/ssl/localhost.key 2> /dev/null
        chown mss.mss %{_sysconfdir}/mss/ssl/localhost.key
    fi

    FQDN=`hostname -f`
    if [ "x${FQDN}" = "x" ]; then
        FQDN=localhost.localdomain
    fi
    
    if [ ! -f %{_sysconfdir}/mss/ssl/localhost.crt ] ; then
        cat << EOF | %{_bindir}/openssl req -new -key %{_sysconfdir}/mss/ssl/localhost.key -x509 -days 365 -set_serial $RANDOM -out %{_sysconfdir}/mss/ssl/localhost.crt 2>/dev/null
--
SomeState
SomeCity
SomeOrganization
SomeOrganizationalUnit
${FQDN}
root@${FQDN}
EOF
        chown mss.mss %{_sysconfdir}/mss/ssl/localhost.crt
    fi
fi
# run setup script for mss-agent (handle bdd creation, upgrade)
%{__python} %{py_puresitedir}/mss/agent/setup_mss.py
# add service
if [ $1 -ge 1 ]; then
    %_post_service mss-agent
    %_post_service mss-www
    # create BDD
    %{__python} %{py_puresitedir}/mss/www/manage.py syncdb --noinput
    chown mss /var/lib/mss/mss-www.db
    /sbin/service mss-agent start
    /sbin/service mss-www start
fi

%post -n mss-modules-mes5
# install/upgrade
if [ $1 -ge 1 ]; then
    /sbin/service mss-agent restart
    /sbin/service mss-www restart
fi
exit 0

%postun -n mss-modules-mes5
# uninstallation
if [ $1 -eq 0 ]; then
    [ -x /etc/init.d/mss-agent ] && /sbin/service mss-agent restart
    [ -x /etc/init.d/mss-www ] && /sbin/service mss-www restart
fi
exit 0

%clean
rm -rf $RPM_BUILD_ROOT

%files -n mss-agents
%defattr(-,root,root,0755)
%exclude %{py_puresitedir}/mss/www/media/img/modules/
%exclude %{py_puresitedir}/mss/www/layout/mes5/
%{_initrddir}/mss-www
%{_initrddir}/mss-agent
%{_sbindir}/mss-agent.py*
%{py_puresitedir}/mss*egg-info/
%{py_puresitedir}/mss/agent/*.py*
%{py_puresitedir}/mss/agent/locale/
%{py_puresitedir}/mss/www/
%{py_puresitedir}/mss/__init__.py*
%attr(0750,mss,root) %{_sharedstatedir}/mss
%{_localstatedir}/log/mss
%{_sysconfdir}/mss/ssl/
%{_datadir}/mdk/desktop/server/*
%{_datadir}/applications/*
%{_datadir}/pixmaps/*

%files -n mss-modules-mes5
%defattr(-,root,root,0755)
%{py_puresitedir}/mss/agent/modules/
%{py_puresitedir}/mss/www/media/img/modules/
%{py_puresitedir}/mss/www/layout/mes5/

%changelog 
* Tue May 25 2010 Jean-Philippe Braun <jpbraun@mandriva.com> 2.0dev
- initial packages

