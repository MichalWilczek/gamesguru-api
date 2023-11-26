# gamesguru-api

An app that serves for scraping multiple web portals to search for the cheapest offers on the market.

## Repository Structure

The repository contains the following folders:
- cron (systemd files for cron jobs for Linux system)
- db (database configuration)
- docker (image configurations for reverse proxy and certbot)
- gamesguru (Django app)
- tests (app unit tests)
- web_client (static files to apply on the frontend side of the program)

## Run Details

The application is configured using `docker-compose.yml`. You might need admin rights to perform the following actions.

To first define admin users and load initial db data, run:
```
docker compose up
docker compose run --rm gamesguru sh -c "python manage.py loaddata gamesguru/products/data/shops.json"
docker compose run --rm gamesguru sh -c "python manage.py createsuperuser"
```

To run scraping, run:
```
docker compose up
docker compose run --rm gamesguru sh -c "python manage.py get_offers"
```

To create an SSL certificate for the 1st time, run:
```
docker compose up
docker compose run --rm certbot /opt/certify-init.sh
```
