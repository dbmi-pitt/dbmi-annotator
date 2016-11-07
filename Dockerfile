############################ POSTGRES ############################

# install postgres db
# FROM ubuntu:14.04

############################ DBMI-ANNOTATOR ############################
# build image from nodejs server
FROM node:0.12.17

# Create dbmi-annotator directory
RUN mkdir -p /home/yin2/dbmi-annotator
WORKDIR /home/yin2/dbmi-annotator

# Install dependencies
COPY package.json /home/yin2/dbmi-annotator/
RUN npm install

# Bundle dbmi-annotator source
COPY . /home/yin2/dbmi-annotator

EXPOSE 3000
CMD [ "npm", "start" ]
