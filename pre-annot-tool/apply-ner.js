// IMPORT
var fs = require('fs'), path = require("path");
var xpath = require('xpath'), parse5 = require('parse5'), xmlser = require('xmlserializer'), dom = require('xmldom').DOMParser;
var Set = require("collections/set");
var Q = require('q');


var HashMap = require('hashmap');

// SET VARS
var MIN_TXT = 30; 
var PRE_POST_LEN = 60;
//var LABEL_HTML_DIR = "../public/DDI-labels/";
var LABEL_HTML_DIR = "html-parser/outputs/";
//var NER_JSON = "NER/NER-outputs.json";
var NER_JSON = "NER/NER-pubmed-sample-outputs.json";
var OUTPUT = "ner-pubmed-json";

parseNERDIR(NER_JSON);

// PARSE NER IN JSON
// @INPUT: file path
// @RETURN: [{setId, drugL}, {xx}]
function parseNERDIR(nerfile){

    try {
        data = fs.readFileSync(nerfile, 'utf-8');
        var nerResults = JSON.parse(data);
        var nerM = new HashMap();
        
        for (m = 0; m < nerResults.length; m++){
            
            item = nerResults[m];
            setid = item.setId;
            
            if (nerM.has(setid)){
                nerM.get(setid).push(item);
            } else {
                nerM.set(setid, []);
            }
        }
        
        var jsonResults = {"nersets":[]};
        
        nerM.forEach(function(item, setid) {

            labelFile = LABEL_HTML_DIR+ setid + ".html";
            selectorsL = findDrugPInLabel(item, labelFile, setid);
            
            if (selectorsL)
                if (selectorsL.length > 0)
                    jsonResults.nersets.push(selectorsL);
        });
        //console.log(JSON.stringify(jsonResults));
        //console.log(nerM.get("08320ea3-8f93-6f04-5d1c-f69af3eb5a81"));
        fs.writeFile(OUTPUT, JSON.stringify(jsonResults), function(err){
            if (err) console.log(err);
        })
        
    } catch(err) {
        console.log("ERROR:" + err);
    }
}


// PARSE DRUG OCCURRENCES IN LABEL
// @INPUT: drugL : JSON list for ner items
// @INPUT: context : File path
// @INPUT: label setid : String
// @RETURN: List of Ranges {startOffset, endOffset, start, end, etc...}

function findDrugPInLabel(drugL, file, setid){

    if (drugL == null || file == null || setid == null) return null;

    var label = fs.readFileSync(file, 'utf-8');
    doc = new dom().parseFromString(label);

    selectorL = [];

    for (i = 0; i < drugL.length; i++){
    //for (var i = 0; i < 20; i++){
        drugItem = drugL[i];

        prefix = drugItem.prefix.replace(/\s/g, ' ');
        suffix = drugItem.suffix.replace(/\s/g, ' ');
        exact = drugItem.exact.replace(/\s/g, ' ');

        drugMatchPattern = "//*[contains(text()[not(parent::script)],'" + exact + "')]";
        var drugNodes = xpath.select(drugMatchPattern, doc);

        if (drugNodes.length > 0){

            for (j = 0; j < drugNodes.length; j++){
                
                if (!drugNodes[j]) continue;
	            cntStr = drugNodes[j].firstChild.data;
	            pathL = getXPath(drugNodes[j]);

                // ignore matches in script or table 
                var isValid = true;
	            pathStr = ""; 

	            for (p = 0; p < pathL.length; p++){
                    if (pathL[p].match(/(table|script|head|h3|h2)/g)){
                        isValid = false;
                        break;
                    }
	    	        pathStr += "/" + pathL[p];
	            }
                
                if (cntStr && isValid){        
                    
                    cntStr = cntStr.replace(/\s/g, ' ');

	                if (cntStr.length > MIN_TXT){
                        
	                    var re = new RegExp(exact,"g");
	                    while (res = re.exec(cntStr)){
		                    startOffset = res["index"];
                            endOffset = startOffset + exact.length;

                            if (startOffset > PRE_POST_LEN)
                                prefixSub = cntStr.substring(startOffset - PRE_POST_LEN, startOffset);
                            else
                                prefixSub = cntStr.substring(0, startOffset);

                            if (cntStr.length - endOffset > PRE_POST_LEN)
                                suffixSub = cntStr.substring(endOffset, endOffset + PRE_POST_LEN);
                            else
                                suffixSub = cntStr.substring(endOffset);

                            if ((prefixSub.indexOf(prefix)>=0 || prefix.indexOf(prefixSub) >=0) && (suffixSub.indexOf(suffix) >= 0 || suffix.indexOf(suffixSub) >=0)){
                            
		                        selectorStr = '{"setid":"' + setid+'","drugname":"' + exact.toLowerCase() + '", "startOffset":"' + startOffset + '","endOffset":"' + endOffset + '", "start":"'+ pathStr + '", "end":"' + pathStr + '", "prefix":"' + prefixSub + '", "suffix":"' + suffixSub + '", "exact":"' + exact + '"}';           

                                selector = JSON.parse(selectorStr);
		                        selectorL.push(selector);
                            }
	                    }
	                }
                }
            }
        } // else {
        //     console.log("[ERROR] didn't match:" + exact);
        // } 
        
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
