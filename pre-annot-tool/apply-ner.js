// IMPORT
var fs = require('fs'), path = require("path");
var xpath = require('xpath'), parse5 = require('parse5'), xmlser = require('xmlserializer'), dom = require('xmldom').DOMParser;
var Set = require("collections/set");
var Q = require('q');


var HashMap = require('hashmap');

// SET VARS
var MIN_TXT = 30; 
var PRE_POST_LEN = 30;
var LABEL_HTML_DIR = "../public/nlabels/";
var NER_JSON = "NER/NER-outputs.json";


parseNERDIR(NER_JSON);

// PARSE NER IN JSON
// @INPUT: file path
// @RETURN: [{setId, drugL}, {xx}]
function parseNERDIR(nerfile){

    data = fs.readFileSync(nerfile, 'utf-8');
    var nerResults = JSON.parse(data);
    var nerM = new HashMap();

    for (i = 0; i < nerResults.length; i++){

        item = nerResults[i];
        setid = item.setId;

        if (nerM.has(setid)){
            nerM.get(setid).push(item);
        } else {
            nerM.set(setid, []);
        }
    }

    var jsonResults = {"nersets":[]};
    
    nerM.forEach(function(item, setid) {
        //console.log(key + " : " + value);
        labelFile = LABEL_HTML_DIR+ setid + ".html";
        selectorsL = findDrugPInLabel(item, labelFile, setid);
        
        if (selectorsL)
            if (selectorsL.length > 0)
                jsonResults.nersets.push(selectorsL);

        
 
    });
    console.log(JSON.stringify(jsonResults));

    //console.log(nerM.get("08320ea3-8f93-6f04-5d1c-f69af3eb5a81"));
}



// PARSE DRUG OCCURRENCES IN LABEL
// @INPUT: drugL : JSON list for ner items
// @INPUT: context : File path
// @INPUT: label setid : String
// @RETURN: List of Ranges {startOffset, endOffset, start, end, etc...}

function findDrugPInLabel(drugL, file, setid){

    //console.log("[INFO] begin search in " + setid);

    if (drugL == null || file == null || setid == null) return null;

    var label = fs.readFileSync(file, 'utf-8');
    doc = new dom().parseFromString(label);

    selectorL = [];

    //for (var j = 0; j < drugL.length; j++){
    for (var j = 0; j < 1; j++){
        drugItem = drugL[j];

        prefix = drugItem.prefix;
        suffix = drugItem.suffix;
        exact = drugItem.exact;

        prefixOffset = prefix.lastIndexOf("\n");
        if (prefixOffset > 0){
            prefix = prefix.substring(prefixOffset + 2);
        }

        suffixOffset = suffix.indexOf("\n");
        if (suffixOffset > 0){
            suffix = suffix.substring(0, suffixOffset);
        }

        drugMatchPattern = "//*[contains(text()[not(parent::script)],'" + exact + "')]";
        var drugNodes = xpath.select(drugMatchPattern, doc);

        if (drugNodes.length > 0){

            for (i = 0; i < drugNodes.length; i++){
                
                if (!drugNodes[i]) continue;

	            cntStr = drugNodes[i].firstChild.data;
	            pathL = getXPath(drugNodes[i]);

                //console.log(drugNodes[i]);

                if (cntStr){        

                    cntStr = cntStr.replace(/\n\n/gm,' ').replace(/\n/gm,' ');
	                if (cntStr.length > MIN_TXT){
                        
	                    pathStr = ""; 
	                    for (j = 0; j < pathL.length; j++){
	    	                pathStr += "/" + pathL[j];
	                    }
                        
	                    var re = new RegExp(exact,"g");
	                    while (res = re.exec(cntStr)){
		                    startOffset = res["index"];
                            endOffset = startOffset + exact.length

                            if (startOffset > PRE_POST_LEN)
                                prefixSub = cntStr.substring(startOffset - PRE_POST_LEN, startOffset);
                            else
                                prefixSub = cntStr.substring(0, startOffset);

                            if (cntStr.length - endOffset > PRE_POST_LEN)
                                suffixSub = cntStr.substring(endOffset, endOffset + PRE_POST_LEN);
                            else
                                suffixSub = cntStr.substring(endOffset);

                            if ((prefixSub.indexOf(prefix) || prefix.indexOf(prefixSub)) && (suffixSub.indexOf(suffix) || suffix.indexOf(suffixSub))){
                            
		                        selectorStr = '{"setid":"' + setid+'","drugname":"' + exact.toLowerCase() + '", "startOffset":"' + startOffset + '","endOffset":"' + endOffset + '", "start":"'+ pathStr + '", "end":"' + pathStr + '", "prefix":"' + prefixSub + '", "suffix":"' + suffixSub + '", "exact":"' + exact + '"}';

                                //console.log(selectorStr);
                                selector = JSON.parse(selectorStr);
		                        selectorL.push(selector);
                            }
	                    }
	                }
                }
            }
        } else {
            console.log("[ERROR] didn't match:" + exact);
        }    
    }
    return selectorL;
}



// GET XPATH OF NODE
function getXPath(node, path) {
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
