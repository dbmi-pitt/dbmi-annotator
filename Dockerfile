############################ DBMI-ANNOTATOR ############################
FROM ubuntu:14.04
MAINTAINER Yifan Ning "yin2@pitt.edu"

# build image from nodejs server
# FROM node:0.12.17

RUN apt-get update
RUN apt-get install -y nodejs npm python-pip libpq-dev python-dev emacs curl jq

RUN update-alternatives --install /usr/bin/node node /usr/bin/nodejs 10

# Create dbmi-annotator directory
RUN mkdir -p /home/dbmi-annotator
WORKDIR /home/dbmi-annotator

# Install dependencies
COPY package.json /home/dbmi-annotator/
RUN npm install

# Bundle dbmi-annotator source
COPY . /home/dbmi-annotator

# Use Production mode configuration for server side requests
COPY config/production.conf /home/dbmi-annotator/config/config.js

# Configure client side requests
RUN ./node_modules/.bin/browserify app.js -o ./public/dbmiannotator/js/app.bundle.js

# Install dependencies for annotation pre-load program
RUN pip install psycopg2 elasticsearch

EXPOSE 3000
CMD [ "npm", "start" ]