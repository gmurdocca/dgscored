# DGScored

DGScored is a Disc Golf league tracking app that:

* Tracks multiple leagues
* Calculates handicaps, adjusted scores, points and ranks per league
* Supports different league structures
* Utilises a simple web interface for data entry and presentation

## Screenshot of the main DGScored page

![Main page](http://imgur.com/eJaUNxG.png "Screenshot of the main DGScored page")

## Screenshot of the Admin page for managing leagues

![Admin page](http://imgur.com/b260sGc.png "Screenshot of the Admin page for managing leagues")

## Installation

### Creating the database during a fresh installation

For a fresh install, you must create the "dgscored" database in MySQL/MariaDB. Run the query:

```sql
create database dgscored;
```


Start the dgscored virtual env from the root of the git repo:

```bash
. $(make env)
```

Create the db cache table:

```bash
dgscored createcachetable
```

Create the database tables:

```bash
dgscored migrate
```

Create admin user:

```bash
dgscored createsuperuser
```

## Starting the dgscored development server:

Start the dgscored virtual env (if not already started):

```bash
. $(make env)
```

Start the web server:

```bash
dgscored runserver
```

Point your browser to the above webserver to use the app.


## Deploying on a Production system

DGScored has been tested on CentOS 7 with Nginx, uWSGI and free SSL using letsencrypt.org.

SELinux was set to permissive mode (ie. disabled, it may function in enforcing mode with the default policy but was not tested) and the server must accept connections on TCP/80 and TCP/443.

To configure this environment on a fresh CentOS 7 system:

```bash
sudo setenforce 0
sudo sed -i 's/SELINUX=enforcing/SELINUX=permissive/' /etc/selinux/config
sudo firewall-cmd --add-service=http --permanent
sudo firewall-cmd --add-service=https --permanent
sudo firewall-cmd --reload
```

To create the RPM for deployment, clone the DGScored Git repository on your CentOS 7 host:

```bash
git clone https://github.com/gmurdocca/dgscored.git
```

RPM build dependencies need to be installed first. To ensure they are:

```bash
sudo yum -y install yum-utils
sudo yum-builddep support/dgscored.spec
```

Now build and install the RPM:

```bash
make rpm
sudo yum -y localinstall dgscored*.rpm
```

Edit the NginX config file /etc/nginx/conf.d/dgscored.conf and configure your server's FQDN as described there in.

Leave the lines beginning with `ssl_certificate` and `ssl_certificate_key` commented out for now because the files these lines reference don't yet exist.

Refer to the comments in the above NginX config file which contain detailed instructions to this effect.

After editing, restart nginx:

```bash
systemctl restart nginx
```

At this point, you should be able to browse to `http://<YOUR_SERVER'S_FQDN>/.well-known/` and see an empty Index directory listing entitled "Index of /.well-known/". This is required to function correctly in order for the next step to complete successfully.

Create your free SSL certificate using certbot:

```bash
sudo yum -y install certbot
sudo certbot certonly --webroot -w /opt/dgscored/certbot/ -d <YOUR_SERVER'S_FQDN>
```

Once certbot runs successfully, edit /etc/nginx/conf.d/dgscored.conf a final time and uncomment the lines beginning with `ssl_certificate` and `ssl_certificate_key`.

Restart NginX to enable SSL and https.

```bash
sudo systemctl restart nginx.service
```

Create an admin user:

```bash
dgscored createsuperuser
```

You should now be able to Browse to your FQDN and use the app.


### Backup and SSL Certificate renewal

To create daily backups of the database and configure automatic SSL certificate renewal:

Create a backup directory:

```bash
mkdir /opt/dgscored/backups
```

Create a file /etc/cron.d/dgscored with contents:

```bash
# Create a DB backup at midnight each day
0 0 * * * root bash --login -c "mysqldump -u root dgscored | gzip > /opt/dgscored/backups/dgscored_prod_backup.sql_$(date +"%Y.%m.%d_%s").gz"
# Delete backups older than 30 days
0 1 * * * root bash --login -c "find /opt/dgscored/backups/ -mtime +30 -type f | xargs rm -rf"
# Renew ssl cert once per month (they expire after 90 days)
0 0 15 * * root bash --login -c "certbot renew | grep -q "No renewals were attempted" || systemctl restart nginx"
```
