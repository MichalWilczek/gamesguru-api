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
        return 301 https://$host$request_uri;
    }
}

server {
    listen      443 ssl;
    server_name ${DOMAIN} www.${DOMAIN};

    ssl_certificate     /etc/letsencrypt/live/${DOMAIN}/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/${DOMAIN}/privkey.pem;

    include     /etc/nginx/options-ssl-nginx.conf;

    ssl_dhparam /vol/proxy/ssl-dhparams.pem;

    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;

    location /static {
        alias /vol/static;
    }

    location / {
        proxy_pass https://${APP_HOST}:${APP_PORT};
        proxy_set_header      Host \$host;
        proxy_set_header      X-Forwarded-Proto \$scheme;
        proxy_set_header      X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_redirect        off;
        client_max_body_size 10M;
    }
}
