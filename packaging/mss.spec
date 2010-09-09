%define name mss
%define version 2.0
%define release 14
%define svnrev 2230
%global username mss
%global groupname mss

%if %mdkversion < 200610
%define py_puresitedir %{_prefix}/lib/python%{pyver}/site-packages/
%endif

Summary: Mandriva Server Setup
Name: %{name}
Version: %{version}
Release: %mkrel %{release}
Source0: %{name}-%{version}-r%{svnrev}.tar.gz
Source1: %{name}.desktop
Source2: %{name}.png
Source3: first_time.html
Source4: logrotate.conf
License: GPLv3 and MIT and ASL 2.0
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
URL: http://www.mandriva.com/
Requires(pre): shadow-utils
Requires(pre): initscripts
Requires(preun): initscripts
Requires: python
Requires: python-django
Requires: python-IPy
Requires: python-OpenSSL
Requires: openssl
Requires: binutils
Obsoletes: mmc-wizard

%description -n	mss-agents
XML-RPC server and web interface

%package -n	mss-modules-mes5
Summary: Mandriva Server Setup modules for MES5
Group: System/Servers
URL: http://www.mandriva.com/
Requires: python
Requires: mss-agents
Obsoletes: mmc-wizard

%description -n	mss-modules-mes5
MES5 Modules for MSS


%prep
%setup -q -n %{name}-%{version}-r%{svnrev}

%build
python setup.py build
cd doc; make html

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

# init scripts
install -d %{buildroot}%{_initrddir}
install -m0755 bin/agent/mss-agent.init %{buildroot}%{_initrddir}/mss-agent
install -m0755 bin/www/mss-www.init %{buildroot}%{_initrddir}/mss-www

# XML-RPC daemon
install -d %{buildroot}%{_sbindir}
install -m0755 bin/agent/mss-agent.py %{buildroot}%{_sbindir}/mss-agent.py

# logrotate configuration
install -d %{buildroot}%{_sysconfdir}/logrotate.d/
install -m0644 %{SOURCE4} %{buildroot}%{_sysconfdir}/logrotate.d/mss-agent

# databases directory
install -d %{buildroot}%{_var}/lib/mss/

# log directory for mss-agent
install -d %{buildroot}%{_logdir}/mss/

# Directory for SSL certificates
install -d %{buildroot}%{_sysconfdir}/mss/ssl/

# Documentation
install -d %{buildroot}%{_datadir}/doc/mss/html/
install -d %{buildroot}%{_datadir}/doc/mss/html/_images/
install -d %{buildroot}%{_datadir}/doc/mss/html/_sources/
install -d %{buildroot}%{_datadir}/doc/mss/html/_static/
install -m0644 README %{buildroot}%{_datadir}/doc/mss/
install -m0644 LICENCE %{buildroot}%{_datadir}/doc/mss/
install -m0644 doc/build/html/*.html %{buildroot}%{_datadir}/doc/mss/html/
install -m0755 doc/build/html/_images/* %{buildroot}%{_datadir}/doc/mss/html/_images/
install -m0755 doc/build/html/_sources/* %{buildroot}%{_datadir}/doc/mss/html/_sources/
install -m0755 doc/build/html/_static/* %{buildroot}%{_datadir}/doc/mss/html/_static/

# .desktop files
install -d %{buildroot}%{_datadir}/mdk/desktop/server/
install -m0644 %{SOURCE1} %{buildroot}%{_datadir}/mdk/desktop/server/%{name}.desktop
install -d %{buildroot}%{_datadir}/applications/
install -m0644 %{SOURCE1} %{buildroot}%{_datadir}/applications/%{name}.desktop

# mss icon
install -d %{buildroot}%{_datadir}/pixmaps/
install -m0644 %{SOURCE2} %{buildroot}%{_datadir}/pixmaps/%{name}.png

# share data 
install -d %{buildroot}%{_datadir}/mss/html/
install -m0644 %{SOURCE3} %{buildroot}%{_datadir}/mss/html/first_time.html

cat > README.urpmi <<EOF
You can access Mandriva Server Setup at https://localhost:8000/
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
Mandriva
MandrivaLinux
${FQDN}
root@${FQDN}
EOF
        chown mss.mss %{_sysconfdir}/mss/ssl/localhost.crt
    fi
    
    # create BDD
    %{__python} %{py_puresitedir}/mss/www/manage.py syncdb --noinput
    chown mss /var/lib/mss/mss-www.db
    
fi
# run setup script for mss-agent (handle bdd creation, upgrade)
%{__python} %{py_puresitedir}/mss/agent/setup_mss.py
# add service
if [ $1 -ge 1 ]; then
    %_post_service mss-agent
    %_post_service mss-www
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
%exclude %{py_puresitedir}/mss/www/media/img/modules/mes5/
%exclude %{py_puresitedir}/mss/www/layout/mes5/
%{_initrddir}/mss-www
%{_initrddir}/mss-agent
%{_sbindir}/mss-agent.py*
%{py_puresitedir}/mss*egg-info/
%{py_puresitedir}/mss/agent/*.py*
%{py_puresitedir}/mss/agent/locale/
%dir %{py_puresitedir}/mss/agent/modules/
%{py_puresitedir}/mss/www/
%{py_puresitedir}/mss/__init__.py*
%attr(0750,mss,root) %{_var}/lib/mss
%{_localstatedir}/log/mss
%{_sysconfdir}/mss/ssl/
%config %{_sysconfdir}/logrotate.d/mss-agent
%{_datadir}/mdk/desktop/server/
%{_datadir}/applications/
%{_datadir}/pixmaps/
%{_datadir}/doc/mss/
%{_datadir}/mss/

%files -n mss-modules-mes5
%defattr(-,root,root,0755)
%{py_puresitedir}/mss/agent/modules/
%{py_puresitedir}/mss/www/media/img/modules/mes5/
%{py_puresitedir}/mss/www/layout/mes5/

%changelog 
* Tue May 25 2010 Jean-Philippe Braun <jpbraun@mandriva.com> 2.0dev
- initial packages

