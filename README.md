# DuopolyDjango
Server part of Duopoly Game. Developed using Django web framework.

__________________________________________________

# How to 

## PostegreSQL install (mac osx)
install postgresql

    brew install postgresql

run pgsql server

    pg_ctl -D /usr/local/var/postgres start

create user and db

    createuser dasein
    createdb DuopolyDB --owner dasein

django migrations
    
    python manage.py makemigrations
    python manage.py migrate

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

