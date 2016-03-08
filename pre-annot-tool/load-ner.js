//var NER_RESULTS = "ners-03012016.json";
var NER_RESULTS = "083-ner";
var ES_CONN = "localhost:9250";

var uuid = require('uuid');

var elasticsearch = require('elasticsearch');
var client = new elasticsearch.Client({
  host: ES_CONN,
  log: 'trace'
});

var fs = require('fs');
var nerResults = fs.readFileSync(NER_RESULTS,"utf-8");
//console.log(nerResults);

var nersets = JSON.parse(nerResults).nersets;

for (i = 0; i < nersets.length; i++){
//for (i = 0; i < 1; i++){
    subL = nersets[i];
    //console.log(subL.length);

    for (j = 0; j < subL.length; j++){
    //for (j = 0; j < 80; j++){
        annot = subL[j];
        //console.log(annot);
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

        uriStr = "http://localhost/DDI-labels/" + annot.setid + ".html";
        uriPost = uriStr.replace(/[\/\\\-\:\.]/g, "");

        //path = "/article[1]/div[1]/div[1]/div[1]" + annot.start
        path = annot.start.replace("/html[1]/body[1]","/article[1]/div[1]/div[1]/div[1]");

        client.index(
            {
                index: 'annotator',
                type: 'annotation',
                id: uuid.v4(),
                body: {
                    "email": "yin2@gmail.com",
                    "created": "2016-03-01", 
                    "updated": "2016-03-01", 
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
                    "user": "alice"
                    
                }
                
            }, function (err, resp) {
                if (err)
                    console.log("[ERROR] " + err)
                else
                    console.log("[INFO] load successfully")
            });


        // client.index(
        //     {
        //         "index": 'annotator',
        //         "type": 'annotation',
        //         "id": uuid.v4(),
        //         "version": 1,
        //         "score": 1,
        //         "source": {
        //             "email": "yin2@gmail.com",
        //             "created": "2016-03-01", 
        //             "updated": "2016-03-01", 
        //             "annotationType": "DrugMention",
        //             "quote": annot.drugname,
        //             "permissions": {},
        //             "ranges": [
        //                 {
        //                     "start": annot.start,
        //                     "end": annot.end,
        //                     "startOffset": annot.startOffset,
        //                     "endOffset": annot.endOffset,
        //                 }
        //             ],
        //             "consumer": "mockconsumer",
        //             "uri": uriPost,
        //             "rawurl": uriStr,
        //             "user": "alice"
        //         }
                
        //     }, function (err, resp) {
        //         console.log("[ERROR] " + err)
        //     });
    }
}

