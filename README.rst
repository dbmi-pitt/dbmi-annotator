===============
AnnotationPress
===============

--------
Overview 
--------
AnnotationPress is designed to provide a user friendly tool that helps scientists annotate scientific claims, data, and evidence in HTML and PDF documents. The current version is configured to annotated drug-drug interactions in both full text journal articles and structured product labeling. This is a particularly challenging domain that required the development of several annotation workflows which we think will be useful for for other scientific domains. A key aspect of AnnotationPress is its use of annotation plug-ins which make the tool is easily adaptable to other annotation use cases. Another distinctive feature is that AnnotationPress implements the `Micropublication <https://jbiomedsem.biomedcentral.com/articles/10.1186/2041-1480-5-28>`_ and `Open Annotation data <http://www.openannotation.org/spec/core/>`_ standards. These standards specify how to relate annotations in target documents about data, methods, and materials to scientific claims.

If you are new to AnnotationPress, please watch our `video <https://goo.gl/kF1aaM>`_ that show two annotation plugins in action.

AnnotationPress is an Apache licensed open source project available on `github <https://github.com/dbmi-pitt/dbmi-annotator>`_. Please contact us if you are interested in contributing to its development, if you would like to request new features, or have any other questions.

---------
Licensing
---------
AnnotationPress is licensed under the Apache License, Version 2.0. See LICENSE for the full license text.


-----------------------
How to run - Production
-----------------------

(1) Install docker(v1.12.3), docker-compose (v1.8.1) and apache (v2.4) server

    Apache2 server configuration
    
    .. code-block::

    # AnnotationPress Docker configuration ###############################
    
    # proxy for docker exposed service at port 8085
    
    ProxyPass /dbmiannotator http://localhost:8085/dbmiannotator
    RewriteRule /dbmiannotator(.*) http://localhost:8085/dbmiannotator$1 [P]

    # proxy for docker exposed service at port 8085 for annotator store
    
    ProxyPass /annotatorstore http://localhost:8085/annotatorstore
    RewriteRule /annotatorstore(.*) http://localhost:8085/annotatorstore$1 [P]

    # stylesheet folder relocate at Document root(dailymed, PMC, wiley)
    
    RewriteRule /dbmiannotator/dailymed(.*) http://localhost/DDI-labels/dailymed$1 [P]
    RewriteRule /dbmiannotator/PMC(.*)_files/(.*) http://localhost/PMC/PMC$1_files/$2 [P]
    RewriteRule /dbmiannotator/wiley(.*)_files/(.*) http://localhost/wiley/wiley$1_files/$2 [P]



(2) Create local volume for postgres and elasticsearch data mount point::

    $ docker volume create --name postgres-volume -d local
    $ docker volume create --name elasticsearch-volume -d local
    $ docker volume create --name elastic-snapshot-volume -d local

(3) Run dbmi-annotator with all dependencies in docker container::

    $ git clone 
    $ cd docker-dbmi-annotator/dbmi-annotator
    $ docker-compose up

Optional: pre-load annotations from csv to DB mpevidence 

    $ python loadDomeoAnnsToRDB.py <pghostname> <pgport> <pguser> <pgpassword> <clean existing data (1: yes, 0: no)>

    ex. $ python loadDomeoAnnsToRDB.py postgres 5432 dbmiannotator dbmi2016 1

    1. optional: clean all data in table
    2. preprocess csv, generate preprocess-domeo.csv
    3. load data into schema mpevidence

Optional: pre-load annotations from postgres DB mpevidence to elasticsearch

    $ docker exec -it dbmi-annotator bash
    $ cd translation/rdb-data-loader
    $ python load-rdb-annotations.py <pg hostname> <pg username> <pg password> <es hostname> <annotation author>

    ex. python load-rdb-annotations.py postgres dbmiannotator dbmi2016 elasticsearch test@gmail.com


For how to build production mode via docker:
https://github.com/dbmi-pitt/docker-dbmi-annotator/blob/master/README

------------------------
How to run - Development
------------------------

Dependences:
^^^^^^^^^^^^

1. Elasticsearch version 1.7 running on port 9200

2. Annotator Store running on port 5000

3. Postgres DB running on port 5432:
   
    create database dbmiannotator
    
    SQL script that create dbmiannotator schema:
    https://github.com/dbmi-pitt/dbmi-annotator/blob/master/db-schema/rdb-postgres-schema.sql

    SQL script that initialize plugin settings:
    https://github.com/dbmi-pitt/dbmi-annotator/blob/master/db-schema/rdb-postgres-initial.sql

4. Apache2 server running on port 80

Installation:
^^^^^^^^^^^^^

1. nodejs packages
``$ npm install``

2. compile browser side JS packages (rerun when made modifications on config/config.js)
``$ browserify app.js -o public/dbmiannotator/js/app.bundle.js``


Configuration:
^^^^^^^^^^^^^^

1.Create config.js 
``$ cp config/config.sample.js config/config.js``

2.Edit config.js based on system environment  

3.Apache2 configurations:

.. code-block::

    #proxy for local nodejs server on port 3000
    RewriteRule /dbmiannotator$ http://localhost:3000/dbmiannotator [P]
    RewriteRule /dbmiannotator/(.*) http://localhost:3000/dbmiannotator/$1 [P]

    #proxy for local annotator store on port 5000
    ProxyPass /annotatorstore http://localhost:5000/
    RewriteRule /annotatorstore(.*) http://localhost:5000$1 [P]  

Run server:
^^^^^^^^^^
.. code-block::

    $ cd dbmi-annotator
    $ nodemon server.js (run '$ npm install -g nodemon', if command is not available)
    $ service apache2 start

    access AnnotationPress through ``'http://localhost/dbmiannotator'``

    
Add documents to annotate:
^^^^^^^^^^
1) Download the HTML using your browser to some place e.g., /path/

2) If needed, rename the file to a more appropriate name. E.g., for PMC articles, it is good to concatenate 'PMC' with the article's PMC identifier. For example, for PMC 1459289 you would:

$ mv  /path/file.html   /path/PMC1459289.html

$ mv  /path/file_files  /path/PMC1459289_files


3) Add html document and related files to apache2 home directory that is relevant for the papers publisher. E.g., for PMC:

$ cp  -r /path/PMC1459289*   /var/www/html/PMC/


4) Register new document by opening up in a text editor the relevant file in the folder dbmi-annotator/article-list/ . For example, for PMC:

$ sublime article-list pmc-list.csv

<you local article identifier> http://localhost/PMC/PMC1459289.html

5) Confirm that you can access the article in your browser using  the link e.g., http://localhost/PMC/PMC4536363.html

6) Now,  refresh the AnnotatorPress in your browser and you should see the new article under the relevant publisher. Click to open.

This should work for all of the publishers we have ensured compatibility between HTML versions of their papers (with their associated files) and our style sheets:

Dailymed
PMC
Wiley
Elsevier
Springer
Sage
Taylor & Francis
Wolters Kluwer


-----------
Directories
-----------

Node.js based program - folder structures
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
config/ - configurations
models/ - represents data, implements business logic and handles storage
controllers/ - defines your app routes and their logic
public/ - contains all static files like images, styles and javascript
views/ - provides templates which are rendered and served by your routes
server.js - initializes the app and glues everything together
package.json - remembers all packages that your app depends on and their versions

reference: https://www.terlici.com/2014/08/25/best-practices-express-structure.html


design
^^^^^^
(1) design/diagram-workspaces/
keep source code of diagram

pencil prototyping tool: *.ep
dia: *.dia
yEd: *.graphml

(2) design/images/
exported images for software design



