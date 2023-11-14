server {
    listen 80;
    server_name ${DOMAIN} www.${DOMAIN};

    location /static {
        alias /vol/web/static;
    }

    location /.well-known/acme-challenge/ {
        root /vol/www/;
    }

    location / {
        # return 301 https://$host$request_uri;
        uwsgi_pass           ${APP_HOST}:${APP_PORT};
        include              /etc/nginx/uwsgi_params;
        client_max_body_size 10M;
    }
}
