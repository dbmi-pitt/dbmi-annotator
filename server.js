
// Load required packages
var express = require('express');

var app = express();

_dirname = "/Users/wenzhang/GitHub/dbmi-annotator/";

// Register all our routes
app.use(express.static(_dirname + 'public'));
var router = express.Router();

// Start the server
app.listen(3000);
