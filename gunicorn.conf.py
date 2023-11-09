keepalive = 5
timeout = 5
access_log_format = '%(h)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'
accesslog = '-'
workers = 4
bind = "127.0.0.1:8000"

# wsgi_app = "gamesguru.wsgi"
# secure_scheme_headers = {
#     'X-FORWARDED-PROTOCOL': 'ssl',
#     'X-FORWARDED-PROTO': 'https',
#     'X-FORWARDED-SSL': 'on'
# }
# worker_class = 'gevent'
# keepalive = 10
# timeout = 120
# access_log_format = '%(h)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'
# accesslog = '-'
# workers = 5
# bind = '0.0.0.0:8000'
