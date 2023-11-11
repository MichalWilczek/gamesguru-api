FROM python:3.10-alpine
LABEL maintainer="MichalWilczek"
ENV PYTHONUNBUFFERED 1

USER nonroot

COPY --chown=nonroot:nonroot run.sh run.sh
COPY --chown=nonroot:nonroot gunicorn.conf.py gunicorn.conf.py
COPY --chown=nonroot:nonroot gamesguru gamesguru
COPY --chown=nonroot:nonroot requirements.txt requirements.txt
COPY --chown=nonroot:nonroot manage.py manage.py

USER root

RUN python -m venv /appenv
ENV VIRTUAL_ENV /appenv
ENV PATH /appenv/bin:$PATH

RUN pip install --upgrade pip && \
    apk add --update --no-cache pcre pcre-dev && \
    apk add --update --no-cache postgresql-client jpeg-dev && \
    apk add --update --no-cache --virtual .tmp-build-deps \
        build-base postgresql-dev musl-dev zlib zlib-dev linux-headers && \
    pip install -r requirements.txt && \
    adduser \
        --disabled-password \
        --no-create-home \
        django-user && \
    mkdir -p /vol/web/static && \
    chown -R django-user:django-user /vol/web/static && \
    chmod -R 755 /vol/web/static && \
    mkdir -p /vol/web/media && \
    chown -R django-user:django-user /vol/web/media && \
    chmod -R 755 /vol/web/media && \
    chmod -R +x run.sh

USER django-user

CMD ["/run.sh"]
