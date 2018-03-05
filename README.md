# DuopolyDjango
Server part of Duopoly Game. Developed using Django web framework.

__________________________________________________

# How to (local) 

## Python dependencies (maybe incomplete)

* django-bulk-update
* django-crispy-forms
* django-bulk-update
* psycopg2-binary
* click
* numpy

## PostgreSQL (MacOs)
install postgresql

    brew install postgresql

run pgsql server

    pg_ctl -D /usr/local/var/postgres start

create user and db

    createuser dasein
    createdb DuopolyRefactor --owner dasein

if you need to reset the table contents
    
    psql DuopolyRefactor -a -f reset.sql

if you need to remove the db
    
    dropdb DuopolyRefactor

## Django 

create superuser
    
    python manage.py createsuperuser
    
django migrations
    
    python manage.py makemigrations
    python manage.py migrate
  
    
Then run the server 
    
    python manage.py runserver
    
Go to the interface at 127.0.0.1:8000 and create a room (room management tab). 
To play alone, trial parameter must be checked.
You should now be able to join the game using the Unity client.

# How to (server) 

## Services required to run the game server in production
* nginx
* duopoly
* postgresql
* postgresql_dir (just once after start up)

The production server runs using the script run_server

## Services required to run the game server in development
* duopoly_django
* postgresql
* postgresql_dir (just once after start up)


The development server runs using the command (contained in duopoly_django service)

    python manage.py 0:8000 |& tee -a log/$(date +%F).log &
  

## Start and stop a service
    sudo systemctl start <service>
    sudo systemctl stop <service>

