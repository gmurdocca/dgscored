# dgscored

DGScored is a Disc Golf league tracking app that supports:

* Track multiple leagues
* Calculates handicaps, adjusted scores, points and ranks per league
* Separate handicaps per league for players
* Simple web interface for data entry and presentation

![Main page](http://imgur.com/eJaUNxG "Screenshot of the main DGScored page")

![Admin page](http://imgur.com/b260sGc "Screenshot of the Admin page for managing leagues")

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

DGScored has been tested on CentOS 7 with Nginx, uWSGI and free SSL using letsencrypt.org

To create an RPM, first clone the Git repository on a CentOS 7 host:

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

Edit /etc/nginx/conf.d/dgscored.conf and configure your server's FQDN as described there in.

Create your free SSL certificate using certbot:

```bash
sudo yum -y install certbot
certbot certonly --webroot -w /opt/dgscored/certbot/ -d <YOUR_SERVER'S_FQDN>
```

Restart NginX

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
0 0 15 * * root bash --login -c "certbot renew"
```

