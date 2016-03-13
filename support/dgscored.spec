Name:           dgscored
Version:        %(date +%Y%m%d%H%M)_%(git rev-list HEAD --count)
Release:        1%{?dist}
Summary:        DGScored is a Disc Golf League tracking web application.
License:        GPLv2
BuildRequires:  rpm-build make python python-pip python-virtualenv git gcc systemd mysql-devel
Requires:       python systemd nginx mysql mysql-server graphviz

%description
DGScored is a Disc Golf League tracking web application.

%global _python_bytecompile_errors_terminate_build 0

%prep
rm -rf %{buildroot}
mkdir -p %{buildroot}/opt/%{name}

%install
# create the virtualenv and install our deps
virtualenv %{buildroot}/opt/%{name}
%{buildroot}/opt/%{name}/bin/python %{buildroot}/opt/%{name}/bin/pip install -U distribute  # some packages require a newer setuptools
%{buildroot}/opt/%{name}/bin/python %{buildroot}/opt/%{name}/bin/pip install -U -r %{srcdir}/requirements.txt
%{buildroot}/opt/%{name}/bin/python %{buildroot}/opt/%{name}/bin/pip install %{srcdir}
%{buildroot}/opt/%{name}/bin/python %{buildroot}/opt/%{name}/bin/dgscored collectstatic --noinput
virtualenv --relocatable %{buildroot}/opt/%{name}
prelink -u %{buildroot}/opt/%{name}/bin/python
rm -f %{buildroot}/opt/%{name}/bin/{activate,activate.*} %{buildroot}/opt/%{name}/lib64

# copy supporting files across
mkdir -p %{buildroot}/usr/lib/systemd/system/ \
         %{buildroot}/etc/nginx/conf.d/ \
         %{buildroot}/usr/local/bin/
cp %{srcdir}/support/%{name}.service %{buildroot}/usr/lib/systemd/system/
cp %{srcdir}/support/nginx.conf %{buildroot}/etc/nginx/conf.d/%{name}.conf
ln -s /opt/%{name}/bin/%{name} %{buildroot}/usr/local/bin

%files
%attr(-, %{name}, %{name}) /opt/%{name}/
%attr(-, root, root) /usr/lib/systemd/system/%{name}.service
%attr(-, root, root) /etc/nginx/conf.d/%{name}.conf
%attr(0755, root, root) /usr/local/bin/%{name}

%pre
/bin/systemctl stop %{name}.service > /dev/null 2>&1 || :
getent group %{name} >/dev/null || groupadd -r %{name}
getent passwd %{name} >/dev/null || \
    useradd -r -g %{name} -d /opt/%{name} -s /sbin/nologin \
    -c "User that runs the %{name} service" %{name}

%post
if [ $1 -eq 1 ] ; then  # Initial installation
    # Set up the service
    /bin/systemctl daemon-reload >/dev/null 2>&1 || :
    /bin/systemctl enable %{name}.service > /dev/null 2>&1 || :
    /bin/systemctl enable nginx.service > /dev/null 2>&1 || :

    # Make sure the default nginx config is removed (it conflicts)
    rm -f /etc/nginx/conf.d/default.conf
fi
# Make sure mysqld is started
/bin/systemctl start mysqld.service > /dev/null 2>&1 || :

# Create the database
mysql -uroot -e "
    CREATE DATABASE IF NOT EXISTS dgscored;
    GRANT ALL ON dgscored.* TO 'writer'@'localhost' IDENTIFIED BY 'writer';
    FLUSH PRIVILEGES;
"

# Syncdb
/opt/%{name}/bin/%{name} syncdb --noinput
/opt/%{name}/bin/%{name} migrate --fake-initial

# Start the services
/bin/systemctl start %{name}.service > /dev/null 2>&1 || :
/bin/systemctl start nginx.service > /dev/null 2>&1 || :

%preun
if [ $1 -eq 0 ] ; then  # Package uninstall, not upgrade
    /bin/systemctl --no-reload disable %{name}.service > /dev/null 2>&1 || :
    /bin/systemctl stop %{name}.service > /dev/null 2>&1 || :
    /bin/systemctl try-restart nginx.service > /dev/null 2>&1 || :
fi

%postun
/bin/systemctl daemon-reload >/dev/null 2>&1 || :
if [ $1 -ge 1 ] ; then  # Package upgrade, not uninstall
    /bin/systemctl try-restart %{name}.service >/dev/null 2>&1 || :
    /bin/systemctl try-restart nginx.service > /dev/null 2>&1 || :
fi
