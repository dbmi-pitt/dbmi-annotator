
// Load required packages
var express = require('express');

var app = express();

_dirname = "/home/yin2/dbmi-annotator/";

// Register all our routes
app.use(express.static(_dirname + 'public'));
var router = express.Router();

// Start the server
app.listen(3000);

app.get('/extractImages', function(req, res) {
    
    var pdfdoc = req.param('pdfdoc');
    
    res.send('pdfdoc: ' + pdfdoc);
    console.log("[INFO] server received request with doc: " + pdfdoc)

    // run pdfimages
    var sys = require('sys')
    var exec = require('child_process').exec;

    function puts(error, stdout, stderr) { sys.puts(stdout) }
    
    exec("mkdir pdf-images/images-" + pdfdoc);
    exec("pdfimages -j public/DDI-pdfs/" +pdfdoc + " pdf-images/images-" + pdfdoc +"/", puts);
    
    console.log("[INFO] extraction complete!");

    
});


// app.get('/viewer.html', function(req, res) {

//     var pdfdoc = req.param('file');
    
//     res.send('pdfdoc: ' + pdfdoc);
//     console.log("server received request in viewer with doc: " + pdfdoc)
// });
