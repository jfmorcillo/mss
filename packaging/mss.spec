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

%package -n	mss-wizard
Summary: Mandriva Server Setup
Group: System/Servers
Requires(pre): shadow-utils
Requires(pre): initscripts
Requires(preun): initscripts
Requires: python
Requires: python-django >= 1.0.4
Requires: python-IPy >= 0.62

%description -n	mss-wizard
XML-RPC server and web interface

%package -n	mss-mes5-modules
Summary: Mandriva Server Setup modules for MES5
Group: System/Servers
Requires: python
Requires: mss-wizard

%description -n	mss-mes5-modules
MES5 Modules for MSS


%prep
%setup -q -n %{name}-%{version}

%build
python setup.py build

%pre -n mss-wizard
getent group %groupname >/dev/null || groupadd -r %groupname
getent passwd %username >/dev/null || \
useradd -r -g %username -d %{_sharedstatedir}/mss -s /sbin/nologin \
-c "User for Mandriva Server Setup" %username
exit 0

%preun -n mss-wizard
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

install -m0755 bin/agent/mss-agent.init %{buildroot}%{_initrddir}/mss-agent
install -m0755 bin/agent/mss-agent.py %{buildroot}%{_sbindir}/mss-agent.py

install -m0755 bin/www/mss-www.init %{buildroot}%{_initrddir}/mss-www

%post -n mss-wizard
if [ $1 -ge 1 ]; then
    %_post_service mss-agent
    %_post_service mss-www
    %{__python} %{py_puresitedir}/mss/www/manage.py syncdb --noinput
    chown mss /var/lib/mss/mss-www.db
    /sbin/service mss-agent start
    /sbin/service mss-www start
fi
exit 0

%post -n mss-mes5-modules
# install/upgrade
if [ $1 -ge 1 ]; then
    /sbin/service mss-agent restart
    /sbin/service mss-www restart
fi
exit 0

%postun -n mss-mes5-modules
# uninstallation
if [ $1 -eq 0 ]; then
    /sbin/service mss-agent restart
    /sbin/service mss-www restart
fi
exit 0

%clean
rm -rf $RPM_BUILD_ROOT

%files -n mss-wizard
%defattr(-,root,root,0755)
%exclude %{py_puresitedir}/mss/www/wizard/config.py*
%exclude %{py_puresitedir}/mss/www/media/img/modules/
%{_initrddir}/mss-www
%{_initrddir}/mss-agent
%{_sbindir}/mss-agent.py*
%{py_puresitedir}/mss*egg-info/
%{py_puresitedir}/mss/agent/*.py*
%{py_puresitedir}/mss/agent/locale/
%{py_puresitedir}/mss/www/
%{py_puresitedir}/mss/__init__.py*
%attr(0750,mss,root) %{_sharedstatedir}/mss

%files -n mss-mes5-modules
%defattr(-,root,root,0755)
%{py_puresitedir}/mss/agent/modules/
%{py_puresitedir}/mss/www/media/img/modules/
%{py_puresitedir}/mss/www/wizard/config.py*

%changelog 
* Tue May 25 2010 Jean-Philippe Braun <jpbraun@mandriva.com> 2.0dev
- initial package

