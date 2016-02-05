module.exports = function(app){

    // extract images from pdf document, save to folder /pdf-images/images-<pdf name>
    // inputs: pdfdoc
    app.get('/extractimages', function(req, res) {
	
	var pdfdoc = req.param('pdfdoc');
	var sys = require('sys')
	var exec = require('child_process').exec;

	// check if pdfdoc parameter appended
	if (pdfdoc){
	
	    var imgDirName = "images-" + pdfdoc;
	    var fileFullPath = "public/DDI-pdfs/" +pdfdoc;

	    // is pdf document avaliable locally
	    fs.stat(fileFullPath, function (err, stats) {
		
		if (err) {
		    res.send(pdfdoc + " is not available at /public/DDI-pdfs/");
		    res.redirect('/main');
		} else {

		    if (stats.isFile()){
			exec("mkdir public/pdf-images/" + imgDirName);
			exec("pdfimages -j " + fileFullPath + " public/pdf-images/"+ imgDirName +"/");
		    } else {
			res.send(pdfdoc + " is not file at /public/DDI-pdfs/");
		    }
		}
	    });
	    

	} else {
	    res.send('pdfdoc parameter is undefined!');
	}
	
    });

    // read images from folder /public/pdf-images/images-<pdf name>
    // inputs: pdf name
    app.get('/readimages', function(req, res) {
	
	var pdfdoc = req.param('pdfdoc');
	
	var dirFullPath = "public/pdf-images/images-" +pdfdoc;
	
	fs.readdir(dirFullPath, function(err, files) {
	    if (err) {
		console.log(err);
		return;
	    }

	    var imageLists = '<ul>';
	    files.forEach(function(fname) {
		
		var imgFullPath = "pdf-images/images-" + pdfdoc + "/" + fname;
                imageLists += '<li><img src="' + imgFullPath + '" width="300"></li>';

	    });
	    imageLists += '</ul>';
	    res.writeHead(200, {'Content-type':'text/html'});
	    res.end(imageLists);
	});
	   	    
    });

    
}
