server {
    listen ${LISTEN_PORT};

    location /static {
        alias /vol/web/static;
    }

    location / {
        uwsgi_pass                  ${APP_HOST}:${APP_PORT};
        include                     /etc/nginx/uwsgi_params;
        client_max_body_size        10M;
        chunked_transfer_encoding   on;
        proxy_set_header            Host ${APP_HOST};
    }
}