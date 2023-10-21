FROM python:3.10-alpine
LABEL maintainer="MichalWilczek"
ENV PYTHONUNBUFFERED 1

USER nonroot

COPY --chown=nonroot:nonroot gamesguru /gamesguru
COPY --chown=nonroot:nonroot scripts /scripts
COPY --chown=nonroot:nonroot requirements.txt /tmp/requirements.txt
COPY --chown=nonroot:nonroot manage.py manage.py

EXPOSE 8000
USER root

RUN python -m venv /py && \
    /py/bin/pip install --upgrade pip && \
    apk add --update --no-cache pcre pcre-dev && \
    # install  postgresql client for psychopg2 \
    apk add --update --no-cache postgresql-client jpeg-dev && \
    # set virtual dependency package and make it temporary to delete it after psychopg2 is installed
    apk add --update --no-cache --virtual .tmp-build-deps \
        build-base postgresql-dev musl-dev zlib zlib-dev linux-headers && \
    /py/bin/pip install -r /tmp/requirements.txt && \
    rm -rf /tmp && \
    # remove temporary dependencies for building -> keep the image as small as possible
    apk del .tmp-build-deps && \
    adduser \
        --disabled-password \
        --no-create-home \
        django-user && \
    mkdir -p /vol/web/static && \
    chown -R django-user:django-user /vol/web/static && \
    chmod -R 755 /vol/web/static && \
    chmod -R +x /scripts

# Update the environment variable
ENV PATH="/scripts:/py/bin:$PATH"

# Change the user from 'root' to 'django-user'
USER django-user

#CMD ["run.sh"]
