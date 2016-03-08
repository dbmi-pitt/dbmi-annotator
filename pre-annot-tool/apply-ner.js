// IMPORT
var fs = require('fs'), path = require("path");
var xpath = require('xpath'), parse5 = require('parse5'), xmlser = require('xmlserializer'), dom = require('xmldom').DOMParser;
var Set = require("collections/set");
var Q = require('q');


var HashMap = require('hashmap');

// SET VARS
var MIN_TXT = 30; 
//var LABEL_HTML_DIR = "Dailymed-SPLs-html/";
var LABEL_HTML_DIR = "../public/DDI-labels/";

var NER_XML_DIR = "NER-results-xml/";


parseNERDIR(NER_XML_DIR);

// PARSE NER XMLS
// @INPUT: dir to NER
// @RETURN: [{setId, drugL}, {xx}]
function parseNERDIR(dir){

    var fs_readdir = Q.denodeify(fs.readdir);
    var fs_stat = Q.denodeify(fs.stat);

    return fs_readdir(dir)
        .then(function(files){
            var promises = files.map(function (file) {
                return fs_stat(path.join(dir,file));
            })
            return Q.all(promises).then(function (stats) { 
                return files;
            })
        })
        .then(function(files){
            var nerM = new HashMap();   
            for (var i = 0; i < files.length; i++ ) {

                var filename = files[i];
                (function(filename){

                    var filepath = NER_XML_DIR + filename;
                    setid = filename.replace("-drugInteractions.txt-PROCESSED.xml","").replace("-clinicalPharmacology.txt-PROCESSED.xml","");

                    data = fs.readFileSync(filepath, 'utf-8');
                    drugS = findNameInXML(data);

                    if (nerM.has(setid)) {
                        try {
                            drugExS = nerM.get(setid);
                            drugL = drugS.toArray();

                            for (k=0; k<drugL.length; k++){
                                drugExS.add(drugL[k]);
                            }
                            nerM.set(setid, drugExS);

                        } catch(ex){
                            console.log(ex);
                        }
                    } else {
                        nerM.set(setid, drugS);           
                    }
  
                })(filename, i)                
            }
            return nerM;
        })
        .then(function(nerM){           
            var jsonResults = {"nersets":[]};

            try {
                nerM.forEach(function(value, key){
                    setid = key.toString();
                    drugL = value.toArray();
                    labelFile = LABEL_HTML_DIR+ setid + ".html";

                    for (var j = 0; j < drugL.length; j++){
                    //for (var j = 0; j < 1; j++){
                        var rangesL = findDrugPInLabel(drugL[j], labelFile, setid);
                        if (rangesL)
                            if (rangesL.length > 0)
                                jsonResults.nersets.push(rangesL);
                    }
                })
                console.log(JSON.stringify(jsonResults));
            } catch(ex){
                console.log(ex);
            }
        })
}

// PARSE DRUG NAMES IN XML CONTENTS
// @INPUT: XML STRING
// @RETURN: SET OF UNIQUE DRUG NAMES
var findNameInXML = function(data){ 

	doc = new dom().parseFromString(data);
	var nameNodes = xpath.select("//name", doc);
	var nameS = new Set([]); 
	
	if (nameNodes){
		for (k = 0; k < nameNodes.length; k++){
			name = nameNodes[k].firstChild.data.trim();
			if (!name.match(".*[,|;|.|(|)].*")){
				nameS.add(name);
			}
		}
        return nameS;
	}
}



// PARSE DRUG OCCURRENCES IN LABEL
// @INPUT: drug name : String
// @INPUT: context : File path
// @INPUT: label setid : String
// @RETURN: List of Ranges {startOffset, endOffset, start, end}

var findDrugPInLabel = function(drug, file, setid){

    if (drug == null || file == null || setid == null) return null;

    file = "083-tidy";
    var label = fs.readFileSync(file, 'utf-8');

    //var request = require('sync-request');
    //var res = request('GET','http://localhost/DDI-labels/08320ea3-8f93-6f04-5d1c-f69af3eb5a81.html');
    //var res = request('GET','http://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=08320ea3-8f93-6f04-5d1c-f69af3eb5a81');
    //var res = request('GET','http://localhost/DDI-labels/test-htmls/08320ea3-8f93-6f04-5d1c-f69af3eb5a81.html');

    //var label = res.getBody().toString();

    doc = new dom().parseFromString(label);

    //innerBody = doc.body;

    //console.log(innerBody)

    drugMatchPattern = "//*[contains(text()[not(name()='script')],'" + drug + "')]";
    
    var drugNodes = xpath.select(drugMatchPattern, doc);
    var rangesL = [];

    for (i = 0; i < drugNodes.length; i++){
    //for (i = 0; i < 1; i++){

        if (!drugNodes[i]){
            continue;
        }

	    cntStr = drugNodes[i].firstChild.data;
	    pathL = getXPath(drugNodes[i]);

        if (cntStr){
        
	        if (cntStr.length > MIN_TXT){
                
	            pathStr = ""; 
	            for (j = 0; j < pathL.length; j++){
	    	        pathStr += "/" + pathL[j];
	            }
                
	            var re = new RegExp(drug.toLowerCase(),"gi");
	            while (res = re.exec(cntStr)){
		            startOffset = res["index"];
		            var rangesStr = '{"setid":"' + setid+'","drugname":"' + drug + '", "startOffset":"' + startOffset + '","endOffset":"' + (startOffset + drug.length) + '", "start":"'+ pathStr + '", "end":"' + pathStr + '"}';
                    ranges = JSON.parse(rangesStr);
		            rangesL.push(ranges);
	            }
	        }
        }
    }
    return rangesL;
}



// GET XPATH OF NODE
var getXPath = function (node, path) {
    path = path || [];
    if(node.parentNode) {
      path = getXPath(node.parentNode, path);
    }

    if(node.previousSibling) {
        var count = 1;
        var sibling = node.previousSibling
        do {
            if(sibling.nodeType == 1 && sibling.nodeName == node.nodeName) {count++;}
            sibling = sibling.previousSibling;
        } while(sibling);
        if(count == 1) {count = null;}
    } else if(node.nextSibling) {
        var sibling = node.nextSibling;
        do {
            if(sibling.nodeType == 1 && sibling.nodeName == node.nodeName) {
                var count = 1;
                sibling = null;
            } else {
                var count = null;
                sibling = sibling.previousSibling;
            }
        } while(sibling);
    }

    if(node.nodeType == 1) {
        path.push(node.nodeName.toLowerCase() + (node.id ? "[@id='"+node.id+"']" : count > 0 ? "["+count+"]" : '[1]'));
        //path.push(node.nodeName.toLowerCase() + (node.id ? "[@id='"+node.id+"']" : count > 0 ? "["+count+"]" : ''));
        //path.push(node.nodeName.toLowerCase() + count > 0 ? "["+count+"]" : '[1]');
    }
    return path;
};



//parseLabelURL();

function parseLabelURL(){

    var request = require('sync-request');

    var res = request('GET','http://localhost/DDI-labels/08320ea3-8f93-6f04-5d1c-f69af3eb5a81.html');
    //var res = request('GET','http://130.49.206.139/DDI-labels/08320ea3-8f93-6f04-5d1c-f69af3eb5a81.html');
    //console.log(res.getBody().toString());
    //label = res;
    //console.log(label);
}
