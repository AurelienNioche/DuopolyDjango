# DuopolyDjango
Server part of Duopoly Game. Based on Django framework.

__________________________________________________

# How to 


## Services required to run the game server in production
* nginx
* duopoly
* postgresql
* postgresql_dir (just once after start up)

## Services required to run the game server in development
* duopoly_django
* postgresql
* postgresql_dir (just once after start up)


The server runs using the command

    python manage.py 0:8000 |& tee -a log/$(date +%F).log &
  

## Start and stop a service
    sudo systemctl start <service>
    sudo systemctl stop <service>

