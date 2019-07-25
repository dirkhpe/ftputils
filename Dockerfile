FROM python:3.7-alpine

RUN adduser -D -u 50001 dirk

WORKDIR /home/dr
RUN mkdir /logs

COPY requirements.txt sftp.py ./
# Alpine Linux requires build environment
# https://github.com/docker-library/python/issues/312
# https://github.com/giampaolo/psutil/issues/872
# build-deps allows to remove build dependencies later on
# gcc, musl-dev and linux-headers are required for psutil
# alpine-sdk is required for pandas
#  libffi-dev openssl-dev is required for gunicorn
RUN apk update
# RUN apk add --no-cache --virtual .build-deps gcc musl-dev linux-headers alpine-sdk
# musl-dev OR glibc-dev
RUN apk add --no-cache gcc musl-dev python3-dev libffi-dev openssl-dev linux-headers make
RUN python -m venv drenv
RUN drenv/bin/pip install --upgrade pip
RUN drenv/bin/pip install -r requirements.txt
# RUN apk del .build-deps gcc musl-dev linux-headers alpine-sdk

COPY properties properties
COPY lib lib
# COPY .env rebuild_sqlite.py get_backup.py murcs_Get.py ./
# COPY fromflask.py config.py boot.sh .env .flaskenv ./
# RUN chmod +x get_backup.py

# RUN chown -R 50001:50005 ./
# RUN chown -R 50001:50005 /logs
# USER dirk

# EXPOSE 5000
# CMD ["/home/bv/get_backup.py"]