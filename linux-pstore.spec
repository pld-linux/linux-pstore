Summary:	Save pstore logs and make room for future logs
Name:		linux-pstore
Version:	0.3
Release:	1
License:	GPL
Group:		Daemons
Source0:	%{name}.py
Source1:	%{name}.crontab
BuildRequires:	rpm-pythonprov
BuildRequires:	rpmbuild(macros) >= 1.268
Requires:	crondaemon
Requires:	mount
Requires:	python3
Requires:	python3-modules
Requires:	python3-psutil
BuildArch:	noarch
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
Copy pstore logs, report to admin and make room for future logs.

%prep
%setup -q -c -T

%build

%install
rm -rf $RPM_BUILD_ROOT

install -d $RPM_BUILD_ROOT{%{_sbindir},/etc/cron.d,/var/log/pstore}

cp -p %{SOURCE0} $RPM_BUILD_ROOT%{_sbindir}/linux-pstore
cp -p %{SOURCE1} $RPM_BUILD_ROOT/etc/cron.d/linux-pstore

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(644,root,root,755)
%attr(755,root,root) %{_sbindir}/linux-pstore
%attr(600,root,root) /etc/cron.d/linux-pstore
%attr(750,root,root) %dir /var/log/pstore
