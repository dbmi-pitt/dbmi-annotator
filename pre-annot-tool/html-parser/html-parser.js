var INPUT_URLS = "input-urls.txt";
var OUTPUT_DIR = "outputs/";

var request = require('request');
var fs = require('fs');
var tidy = require('htmltidy').tidy;
var path = require('path');

var lineReader = require('readline').createInterface({
    input: fs.createReadStream(INPUT_URLS)
});

// read urls
lineReader.on('line', function (line) {
    console.log(line);
    
    // get html from url
    request(line, function(err, res, body){

        labelDecode = body.replace(/&amp;/g,'&').replace(/&nbsp;/g,' ');        

        // normalize html source
        tidy(labelDecode, function(err, html) {
            if (err){
                console.log(err);
            }

            // write to file
            var file = "sample.html";
            if (line.indexOf("dailymed") > 0){
                if (line.indexOf("setid=") > 0)
                    file = OUTPUT_DIR + line.replace("http://dailymed.nlm.nih.gov/dailymed/lookup.cfm?setid=","") + ".html";
                else if (line.indexOf("archives") > 0)
                    file = OUTPUT_DIR + line.replace("http://dailymed.nlm.nih.gov/dailymed/archives/fdaDrugInfo.cfm?archiveid=","archiveid-") + ".html";
                else
                    console.log("[ERROR] dailymed url not resolved!");
            } else {
                file = OUTPUT_DIR + line + ".html";
            }

            fs.writeFile(path.join(__dirname, file), html, function(err) {
                if(err) {
                    return console.log(err);
                }
                
                console.log("Saved " + file);
            }); 

        });


    });
    
});








