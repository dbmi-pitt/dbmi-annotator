/*************************************************************************
 * Copyright 
 *
 *************************************************************************
 *
 * @description
 * apply result from NER program, append OA selector fields to annotation item, converts to json format for annotation preload purpose
 * 
 * @author
 * Yifan Ning
 *
 *************************************************************************/


// IMPORT=================================================================
var fs = require('fs'), path = require("path");
var xpath = require('xpath'), parse5 = require('parse5'), xmlser = require('xmlserializer'), dom = require('xmldom').DOMParser;
var Set = require("collections/set");
var q = require('q');
var HashMap = require('hashmap');
var tidy = require('htmltidy').tidy;

// SET VARS=================================================================
var MIN_TXT = 10; 
var PRE_POST_LEN = 60;
//var LABEL_HTML_DIR = "../public/DDI-labels/";
//var LABEL_HTML_DIR = "html-parser/outputs/";
//var NER_JSON = "NER/NER-outputs.json";
//var NER_JSON = "NER/NER-pubmed-sample-outputs.json";


// MAIN=================================================================

var args = process.argv.slice(2);
if (args.length == 3) {
    var NER_JSON = args[0];
    var LABEL_HTML_DIR = args[1];

    if (args[2] == "dailymed"){
        var OUTPUT = "ner-dailymed-json";
    } else if (args[2] == "pubmed") {
        var OUTPUT = "ner-pubmed-json";
    }

    parseNERDIR(NER_JSON);

} else {
    console.log("RUN: node apply-ner.js <ner-results (ex. NER/NER-outputs.json)> <html label directory> <options: pubmed or dailymed>");
    process.exit(1);
}



// PARSE NER IN JSON
// @INPUT: file path
// @RETURN: [{setId, drugL}, {xx}]
function parseNERDIR(nerfile){

    try {
        data = fs.readFileSync(nerfile, 'utf-8');
        var nerResults = JSON.parse(data);

        // hashmap for document and list of drug names
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

            var label = fs.readFileSync(labelFile, 'utf-8');

            tidy(label, function(err, html) {
                if (err){
                    console.log(err);
                }

                selectorsL = findDrugPInLabel(item, html, setid);
                if (selectorsL)
                    if (selectorsL.length > 0)
                        jsonResults.nersets.push(selectorsL);
                else 
                    console.log("WARNING: find drug in html failed - file: " + labelFile);

                fs.writeFile(OUTPUT, JSON.stringify(jsonResults), function(err){
                    if (err) console.log(err);
                })
            });
            
        });
        
    } catch(err) {
        console.log("ERROR:" + err);
    }
}


// PARSE DRUG OCCURRENCES IN LABEL
// @INPUT: drugL : JSON list for ner items
// @INPUT: context : File path
// @INPUT: label setid : String
// @RETURN: List of Ranges {startOffset, endOffset, start, end, etc...}

function findDrugPInLabel(drugL, dochtml, setid){

    if (drugL == null || dochtml == null || setid == null) return null;

    doc = new dom().parseFromString(dochtml);        
    selectorL = [];
        
    for (i = 0; i < drugL.length; i++){
        //for (var i = 0; i < 20; i++){
        drugItem = drugL[i];
        
        prefix = drugItem.prefix.replace(/\s/g, ' ');
        suffix = drugItem.suffix.replace(/\s/g, ' ');
        exact = drugItem.exact.replace(/\s/g, ' ');
        
        drugMatchPattern = "//*[contains(text()[not(parent::script)],'" + exact + "')]";
        // xpath search drug instances on page
        var drugNodes = xpath.select(drugMatchPattern, doc);
        
        if (drugNodes.length > 0){
            
            for (j = 0; j < drugNodes.length; j++){
                
                if (!drugNodes[j]) continue;
	            cntStr = drugNodes[j].firstChild.data;
                
                // get xpath from dom node
	            pathL = getXPath(drugNodes[j]);
                
                // ignore matches in script or table 
                var isValid = true;
	            pathStr = ""; 
                
                // skip matches in table, script, head, etc
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
                            
                            // if over lapping with prefix & suffix from NER 
                            if ((prefixSub.indexOf(prefix)>=0 || prefix.indexOf(prefixSub) >=0) && (suffixSub.indexOf(suffix) >= 0 || suffix.indexOf(suffixSub) >=0)){
                                
		                        selectorStr = '{"setid":"' + setid+'","drugname":"' + exact.toLowerCase() + '", "startOffset":"' + startOffset + '","endOffset":"' + endOffset + '", "start":"'+ pathStr + '", "end":"' + pathStr + '", "prefix":"' + prefixSub + '", "suffix":"' + suffixSub + '", "exact":"' + exact + '"}';           
                                
                                selector = JSON.parse(selectorStr);
		                        selectorL.push(selector);
                            }
	                    }
	                } else {
                        console.log("WARNING - missed NER");
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
