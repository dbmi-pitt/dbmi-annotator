var request = require('request');
var fs = require('fs');
var cheerio = require('cheerio');
var path = require('path');

var INPUT_URLS = "input-urls.txt";
var OUTPUT_DIR = "outputs/";

var lineReader = require('readline').createInterface({
    input: fs.createReadStream(INPUT_URLS)
});


lineReader.on('line', function (url) {
    console.log(url);
    if (url.indexOf('http') >= 0){
        request(url, function(err, res, htmlbody){
            
            $ = cheerio.load(htmlbody);

            html = $('.tsec').text()
            file = url.replace("http://www.ncbi.nlm.nih.gov/pmc/articles/","") + ".txt";
            
            if (html){
                
                fs.writeFile(path.join(OUTPUT_DIR, file), html, function(err) {
                        if(err) {
                            return console.log(err);
                        }
                    console.log("Saved " + file);
                }); 
            }
            
        }, {decodeEntities: true});
    }
});

