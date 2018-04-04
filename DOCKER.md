# Using with Docker

Use [Docker Compose][1].

## Setup

Create Docker images by running:

    docker-compose up

Exit by pressing `Ctrl-C`. Create required database tables by running:

    docker-compose run web python3 manage.py migrate

Create super user for admin site:

    docker-compose run web python3 manage.py createsuperuser

## Running

Start:

    docker-compose up

Stop:

Press `Ctrl-C`.

## Invoking Django commands

    docker-compose run web python3 manage.py <command>

## Manual database handling

### Connect to database

Check if postgres image is running by `docker ps`. If not, you can start it simply by:

    docker-compose start db

Then run:

    docker-compose run db psql -h db -U postgres

If you want to recreate whole database:

    DROP SCHEMA public CASCADE;
    CREATE SCHEMA public;

Then exit from psql shell and run:

    # If you need to make new migration files
    docker-compose run web python3 manage.py makemigrations

    docker-compose run web python3 manage.py migrate
    docker-compose run web python3 manage.py createsuperuser

### Rebuild Web Docker Image

    docker-compose build

### Test data

How to create a new dump:

    docker-compose run web python3 manage.py dumpdata --indent 2 > fixtures/test01.json
    # Another example
    docker-compose run web python3 manage.py dumpdata --indent 2 admin auth.user avdb > fixtures/test02.json

How to load the dump:

    docker-compose run web python3 manage.py loaddata fixtures/test01.json

## Destroying Containers

This will destroy Docker containers, including all data in database:

    docker-compose down

[1]: https://docs.docker.com/compose/
