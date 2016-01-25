//configuration
_dirname = "/home/yin2/dbmi-annotator/";

// Load required packages
fs = require('fs');
var express = require('express');

var app = express();
var dbOperations = require('./models/dbOperations.js');

// Register all our routes
app.use(express.static(_dirname + 'public'));
var router = express.Router();

// Start the server
app.listen(3000);

app.get('/validateUser', function(req, res) {
    console.log('[INFO] user validation');
    dbOperations.validateUser(req,res);
});


app.get('/extractImages', function(req, res) {
    
    var pdfdoc = req.param('pdfdoc');
    
    console.log("[INFO] server received request with doc: " + pdfdoc)

    // run pdfimages
    var sys = require('sys')
    var exec = require('child_process').exec;

    var imgDirName = "images-" + pdfdoc;
    exec("mkdir public/pdf-images/" + imgDirName);
    exec("pdfimages -j public/DDI-pdfs/" +pdfdoc + " public/pdf-images/"+ imgDirName +"/");
    console.log("[INFO] extraction complete!");

    var img = fs.readFileSync('public/pdf-images/' + imgDirName + "/-000.jpg");
    res.writeHead(200, {'Content-Type': 'image/jpg' });
    res.end(img, 'binary');
    
    res.send('pdfdoc: ' + pdfdoc);
    
});
