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

# Use Production mode configuration
COPY config/production.conf /home/yin2/dbmi-annotator/config/config.js

RUN ./node_modules/.bin/browserify config/production-app.js -o /home/yin2/dbmi-annotator/public/dbmiannotator/js/app.bundle.js

EXPOSE 3000
CMD [ "npm", "start" ]
