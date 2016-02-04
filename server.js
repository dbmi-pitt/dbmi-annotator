// set up
_dirname = "/home/yin2/dbmi-annotator/";
var port     = process.env.PORT || 3000;

// Load packages
fs = require('fs');
var express = require('express');
var passport = require('passport');
var flash = require('connect-flash');

var morgan       = require('morgan');
var cookieParser = require('cookie-parser');
var bodyParser   = require('body-parser');
var session      = require('express-session');

var app = express();

app.use(express.static('public'));

app.use(morgan('dev')); // log every request to the console
app.use(cookieParser()); // read cookies (needed for auth)
app.use(bodyParser()); // get information from html forms

// enable template engine ejs
app.set('view engine', 'ejs'); 

// bring sequelize in
var Sequelize = require('sequelize');
var conStr = require('./config/config');
var sequelize = new Sequelize(conStr, {dialect:'postgres', define:{freezeTableName:true, timestamps: false} });
// model initialize
var user = require('./models/user')(sequelize, Sequelize);

user.sync();

// required for passport
app.use(session({ secret: 'dbmi2016' })); // session secret
app.use(passport.initialize());
app.use(passport.session()); // persistent login sessions
app.use(flash()); 

require('./config/passport')(passport, user); 
require('./controllers/routes')(app, passport);
require('./controllers/pdf-image-extract')(app);

app.listen(port);










