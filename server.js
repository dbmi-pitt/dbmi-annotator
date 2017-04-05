/* Copyright 2016-2017 University of Pittsburgh

 Licensed under the Apache License, Version 2.0 (the "License");
 you may not use this file except in compliance with the License.
 You may obtain a copy of the License at

     http:www.apache.org/licenses/LICENSE-2.0

 Unless required by applicable law or agreed to in writing, software
 distributed under the License is distributed on an "AS IS" BASIS,
 WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 See the License for the specific language governing permissions and
 limitations under the License. */

// SET UP
var _dirname = "/home/yin2/dbmi-annotator/";
var config = require('./config/config');
var pg = require('pg');

// Load packages
fs = require('fs');
var express = require('express');
var passport = require('passport');
var flash = require('connect-flash');

var morgan       = require('morgan');
var cookieParser = require('cookie-parser');
var bodyParser   = require('body-parser');
var session      = require('express-session');
var expressValidator = require('express-validator');

// bring sequelize in
var Sequelize = require('sequelize');
var sequelize = new Sequelize(config.postgres, {dialect:'postgres', define:{freezeTableName:true, timestamps: false}});

// Initialize postgres DB schema - dbmiannotator
var client = new pg.Client(config.postgres);

var schemasql = fs.readFileSync('./db-schema/rdb-postgres-schema.sql').toString();
var initsql = fs.readFileSync('./db-schema/rdb-postgres-initial.sql').toString();

client.query(schemasql);

// model initialize
var user = require('./models/user')(sequelize, Sequelize);


//var plugin = require('./models/plugin')(sequelize, Sequelize);
// user.sync();
// plugin.sync();

var app = express();
app.use(morgan('dev')); // log every request to the console
app.use(cookieParser()); // read cookies (needed for auth)
app.use(bodyParser()); // get information from html forms
app.use(expressValidator());

app.use(express.static('public'));
app.set('view engine', 'ejs'); 

// required for passport
app.use(session({ secret: 'dbmi2020'}));

//app.use(session({ secret: 'dbmi2020', cookie: {expires: new Date(Date.now() + 3600000)}})); // session secret
// maxAge: new Date(Date.now() + 3600000) cause session expire one hr after server start 
app.use(passport.initialize());
app.use(passport.session()); // persistent login sessions
app.use(flash()); 

require('./config/passport')(passport, user); 
require('./controllers/routes')(app, passport);
require('./controllers/pdf-image-extract')(app);

app.listen(config.annotator.port);










