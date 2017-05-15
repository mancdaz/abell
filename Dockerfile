FROM python:2.7.13-alpine
MAINTAINER Michael Porras

ENV LANG en_US.UTF-8


RUN mkdir -p /var/www/abell
WORKDIR /var/www/abell
ADD requirements.txt /var/www/abell/
RUN pip install -r requirements.txt
ADD . /var/www/abell
