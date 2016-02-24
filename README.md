# dgscored

DGScored is a Disc Golf league tracking app that supports:

* Track multiple leagues
* Calculates handicaps, adjusted scores, points and ranks per league
* Separate handicaps per league for players
* Simple web interface for data entry and presentation

## Installation

### Creating the database during a fresh installation

For a fresh install, you must create the "dgscored" database in MySQL/MariaDB. Run the query:

    create database dgscored;

Start the dgscored virtual env from the root of the git repo:

    . $(make env)

Create the database tables:

    dgscored migrate

Create admin user:

    dgscored createsuperuser


## Starting the dgscored development server:

Start the dgscored virtual env (if not already started):

    . $(make env)

Start the web server:

    dgscored runserver

Point your browser to the above webserver to use the app.
