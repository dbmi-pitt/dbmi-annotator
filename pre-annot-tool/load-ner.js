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

 /* description
 load NER in json to elasticsearch for dbmi-annotator pre-annotate drug mentions */

// IMPORT=================================================================
var config = require('./../config/config.js');
var HOSTNAME = config.elastico.host;
var ES_CONN = config.elastico.host + ":" + config.elastico.port;
var q = require('q');
var uuid = require('uuid');
var fs = require('fs');


// ELASTICO=================================================================
var elasticsearch = require('elasticsearch');
var client = new elasticsearch.Client({
  host: ES_CONN
  //log: 'trace'
});

//MAIN=================================================================
var args = process.argv.slice(2);
if (args.length == 3) {

    var email = args[2];

    if (args[1] == "dailymed" || args[1] == "pubmed"){
        if (args[1] == "dailymed")
            var NER_RESULTS = "ner-dailymed-json";
        else if (args[1] == "pubmed") {
            var NER_RESULTS = "ner-pubmed-json";
        } 
        var nerResults = fs.readFileSync(NER_RESULTS,"utf-8");
        var nersets = JSON.parse(nerResults).nersets;
        loadNERs(nersets, args[1], email);
    }
    else {
        console.log("RUN: node load-ner.js <ner-results (ex. ner-pubmed-json)> <options: pubmed or dailymed> <user email (ex. yin2@gmail.com)>");
        process.exit(1);
    } 
} else {
    console.log("RUN: node load-ner.js <ner-results (ex. ner-pubmed-json)> <options: pubmed or dailymed> <user email (ex. yin2@gmail.com)>");
    process.exit(1);
}


function loadNERs(nersets, sourceType, email){

    for (i = 0; i < nersets.length; i++){
    //for (i = 0; i < 1; i++){
        subL = nersets[i];
        
        for (j = 0; j < subL.length; j++){
        //for (j = 0; j < 10; j++){
            annotation = subL[j];
            if (annotation){
                uriStr = "";
                if (sourceType == "pubmed")
		            // load for alive PMC articles
                    // uriStr = "http://www.ncbi.nlm.nih.gov/pmc/articles/" + annotation.setid;

		            // load for local pmc html articles
		            uriStr = "http://localhost/dbmiannotator/" + annotation.setid + ".html";
                else if (sourceType == "dailymed")
                    uriStr = "http://" + HOSTNAME + "/DDI-labels/" + annotation.setid + ".html";
                else {
                    console.log("[ERROR] sourceType wrong: " + sourceType);
                    process.exit(1);
                }              
                loadNewAnnotation(annotation, uriStr, email);
            }
        }
    }
}

function loadNewAnnotation(annotation, uriStr, email){

    console.log("[INFO]: begin check for " + annotation.exact + " | " + email);
    uriPost = uriStr.replace(/[\/\\\-\:\.]/g, "");

    q.nfcall(
        client.search(
            {
                index: 'annotator',
                type: 'annotation',
                body:{
                    query : {
                        bool : {
                            must : [
                                {
                                    match: {
                                        "email": email                           
                                    }
                                },
                                {
                                    match: {
                                        "uri": uriPost                           
                                    }
                                },
                                {
                                    match: {
                                        "prefix": annotation.prefix                           
                                    }
                                },
                                {
                                    match: {
                                        "exact": annotation.exact                           
                                    }
                                },
                                {
                                    match: {
                                        "suffix": annotation.suffix                  
                                    }
                                }
                            ]
                        }
                    }
                }
            }).then(function (resp){
                var hits = resp.hits.hits;
                if (hits.length > 0){
                    console.log("[EXITS] " + annotation.exact);
                    //console.log(hits);
                    return true;
                } else {
                    console.log("[NOT EXITS] " + annotation.exact);
                    return false;
                }
            }).then(function (isExists){
                if (!isExists){
                    loadAnnotation(annotation, uriStr, email);
                }
            })
    );
}


function loadAnnotation(annotation, uriStr, email){

    if (annotation == null){
        console.log("[ERROR] annotation is null!");

        if (annotation.setid == null || annotation.drugname == null || annotation.startOffset == null || annotation.endOffset == null || start == null || end == null)
            console.log("[ERROR] annot attributes incompelete!");
        return null;
    } else {
        uriPost = uriStr.replace(/[\/\\\-\:\.]/g, "");
        path = annotation.start.replace("/html[1]/body[1]","");        

        console.log("[INFO]: begin load for " + annotation.exact);
        var datetime = new Date();
        client.index(
            {
                index: 'annotator',
                type: 'annotation',
                id: uuid.v4(),
                body: {    // annotatorJs fields for drug Mention
                    "email": email,
                    "created": datetime, 
                    "updated": datetime, 
                    "annotationType": "DrugMention",
                    "permissions": {
			"read": ["group:__consumer__"]
		    },
                    "argues": {
                        "hasTarget": {
                            "hasSelector": {
                                "@type": "TextQuoteSelector",
                                "exact": annotation.exact,
                                "prefix": annotation.prefix,
                                "suffix": annotation.suffix
                            }
                        },
                        "ranges": [
                            // {
                            //     "start": path,
                            //     "end": path,
                            //     "startOffset": parseInt(annotation.startOffset),
                            //     "endOffset": parseInt(annotation.endOffset),
                            // }
                        ],
                        "supportsBy": []
                    },
                    "consumer": "mockconsumer",
                    "uri": uriPost,
                    "rawurl": uriStr,
                    "user": "alice"
                }
            }, function (err, resp) {
                if (err)
                    console.log("[ERROR] " + err);
                else
                    console.log("[INFO] load successfully");
            });
    }
}


