var config = require('./../config/config.js');
var HOSTNAME = config.elastico.host;
var ES_CONN = config.elastico.host + ":" + config.elastico.port;

var NER_RESULTS = "ner-resutls-json";

var uuid = require('uuid');
//var USER_EMAIL = "yin2@gmail.com"
var USER_EMAIL = "123@123.com"

var elasticsearch = require('elasticsearch');
var client = new elasticsearch.Client({
  host: ES_CONN
  //log: 'trace'
});


var fs = require('fs');
var nerResults = fs.readFileSync(NER_RESULTS,"utf-8");
var nersets = JSON.parse(nerResults).nersets;

for (i = 0; i < nersets.length; i++){
//for (i = 0; i < 1; i++){
    subL = nersets[i];

    for (j = 0; j < subL.length; j++){
        annot = subL[j];

        if (annot){
            es_index(annot);
        }
    }
}


function es_index(annot){

    if (annot == null){
        console.log("[ERROR] annot is null!");

        if (annot.setid == null || annot.drugname == null || annot.startOffset == null || annot.endOffset == null || start == null || end == null)
            console.log("[ERROR] annot attributes incompelete!");
        return null;
    } else {

        uriStr = "http://" + HOSTNAME + "/DDI-labels/" + annot.setid + ".html";
        uriPost = uriStr.replace(/[\/\\\-\:\.]/g, "");

        path = annot.start.replace("/html[1]/body[1]","/article[1]/div[1]/div[1]/div[1]");
        //path = annot.start.replace("/html[1]/body[1]","/article[1]/div[1]/div[1]");

        var isExists = false;
        console.log("[INFO]: begin check for " + annot.exact);

        // client.search(
        //     {
        //         index: 'annotator',
        //         type: 'annotation',
        //         body:{
        //             query : {
        //                 match: {
        //                     "email": USER_EMAIL                            
        //                 },
        //                 match: {
        //                     "uri": uriPost                            
        //                 },
        //                 match: {
        //                     "prefix": annot.prefix
        //                 },
        //                 match: {
        //                     "exact": annot.exact                            
        //                 }
        //             }
        //         }

        //     }).then(function (resp){
        //         var hits = resp.hits.hits;
        //         console.log("results:" + hits.length);
                
        //         if (hits.length > 0)
        //             console.log("[EXITS]");
        //         else {
        console.log("[NOT EXITS]");
        console.log("[INFO]: begin load for " + annot.exact);
        var datetime = new Date();
        client.index(
            {
                index: 'annotator',
                type: 'annotation',
                id: uuid.v4(),
                body: {    // annotatorJs fields for drug Mention
                    "email": USER_EMAIL,
                    "created": datetime, 
                    "updated": datetime, 
                    "annotationType": "DrugMention",
                    "quote": annot.drugname,
                    "permissions": {},
                    "ranges": [
                        {
                            "start": path,
                            "end": path,
                            "startOffset": parseInt(annot.startOffset),
                            "endOffset": parseInt(annot.endOffset),
                        }
                    ],
                    "consumer": "mockconsumer",
                    "uri": uriPost,
                    "rawurl": uriStr,
                    "user": "NER",
                    target: {   //for OA text quote selector (JSON-LD)
                        "source" : uriStr,
                        "selector" : {
                            "@type": "TextQuoteSelector",
                            "exact": annot.exact,
                            "prefix": annot.prefix,
                            "suffix": annot.suffix
                        }
                    }
                }
            }, function (err, resp) {
                if (err)
                    console.log("[ERROR] " + err)
                else
                    console.log("[INFO] load successfully")
            });
    }
}


