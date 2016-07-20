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
var htmltidyOptions = require('htmltidy-options');

// SET VARS=================================================================
// var MIN_TXT = 10; 
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

        // hashmap for keep mappings of document and list of NERs
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

            tidy(label, htmltidyOptions['Kastor tidy - XHTML Clean page UTF-8'], function(err, html) {

                if (err){
                    console.log(err);
                }
                // search NERs in html document
                console.log("[INFO] Begin document: " + setid);
                selectorsL = findNERsInDoc(item, html, setid);
                if (selectorsL != null) {
                    if (selectorsL.length > 0) {
                        jsonResults.nersets.push(selectorsL);
                    }
                }
                else 
                    console.log("[WARNING] find drug in html failed - file: " + labelFile);

                fs.writeFile(OUTPUT, JSON.stringify(jsonResults), function(err){
                    if (err) console.log(err);
                })
            });
        
        });
        
    } catch(err) {
        console.log("[ERROR]" + err);
    }
}


// PARSE DRUG OCCURRENCES IN LABEL
// @INPUT: drugL : JSON list for ner items
// @INPUT: context : File path
// @INPUT: label setid : String
// @RETURN: List of Ranges {startOffset, endOffset, start, end, etc...}

function findNERsInDoc(drugNERsL, dochtml, setid){

    if (drugNERsL == null || dochtml == null || setid == null) return null;

    doc = new dom().parseFromString(dochtml);        
    var selectorL = []; // OA and xpath selectors
    var notFoundNERs = new Set(); // keep list of miss matched NER drug names

    console.log("total NER: " + drugNERsL.length);

    for (i = 0; i < drugNERsL.length; i++){ // loop NERs identified in document
    //for (var i = 0; i < 3; i++){
        drugItem = drugNERsL[i];
        
        // oaselector from NER results
        prefix = drugItem.prefix.replace(/\s/g, ' ');
        suffix = drugItem.suffix.replace(/\s/g, ' ');
        exact = drugItem.exact.replace(/\s/g, ' ');

        if (notFoundNERs.has(exact))
            continue;
        
        // narrow down for testing 
        // if (exact != "acetonitrile" && exact != "warfarin") 
        //     continue;
        
        //drugMatchPattern = "//*[contains(text(),\"" + exact + "\")]";
        //var drugNodes = xpath.select(drugMatchPattern, doc);

        // get all p nodes
        var pNodes = doc.getElementsByTagName("p");
        var re = new RegExp(exact,"g");
        allSelectorL = [];  // NER if exact prefix/suffix match not found
        matchedSelectorL = []; // prefix/suffix match
        isNERMatchFound = false;

        for (j = 0; j < pNodes.length; j++) {     

            pCntStr = pNodes[j].textContent;
            pPathStr = getFormattedXPathFromNode(pNodes[j]);               

            if (pCntStr != null) {

                while (res = re.exec(pCntStr)){
                    //console.log(pCntStr);
		            startOffset = res["index"];
                    endOffset = startOffset + exact.length;
                    
                    if (startOffset > PRE_POST_LEN)
                        prefixSub = pCntStr.substring(startOffset - PRE_POST_LEN, startOffset);
                    else
                        prefixSub = pCntStr.substring(0, startOffset);
                            
                    if (pCntStr.length - endOffset > PRE_POST_LEN)
                        suffixSub = pCntStr.substring(endOffset, endOffset + PRE_POST_LEN);
                    else
                        suffixSub = pCntStr.substring(endOffset);

                    jsonSelector = JSON.stringify({setid: setid, drugname: exact.toLowerCase() , startOffset:  startOffset  ,endOffset:  endOffset  , start: pPathStr  , end:  pPathStr  , prefix:  prefixSub , suffix: suffixSub, exact:  exact });
                    
                    if (!notFoundNERs.has(exact)) {
                        allSelectorL.push(JSON.parse(jsonSelector));              
                    }
                    // DEBUGING ====================
                    // if (pCntStr.indexOf("mg intravenous dose of rifampin. Rifampin did not significantly alter R- or S-") > 0 && suffix.indexOf("area under the concentration-time curve (AUC) from") > 0) {
                    //     console.log("subPrefix: |" + prefixSub + "|");
                    //     console.log("subSuffix: |" + suffixSub + "|");
                    // }                       
                    
                    // if over lapping with prefix & suffix from NER 
                    if ((prefixSub.indexOf(prefix)>=0 || prefix.indexOf(prefixSub) >=0) && (suffixSub.indexOf(suffix) >= 0 || suffix.indexOf(suffixSub) >=0)){           
                        matchedSelectorL.push(JSON.parse(jsonSelector));
                        isNERMatchFound = true;                            
                    }                    
                }                                                              
            }
        }
    
        // exact NER found and haven't added all occurrances yet 
        if (isNERMatchFound && !notFoundNERs.has(exact)) { 
            //console.log("[INFO] NER found for exact: " + exact);
            //console.log("prefix: " + prefix);
            //console.log("suffix: " + suffix);
            selectorL = selectorL.concat(matchedSelectorL);
            matchedSelectorL = [];
        } else if (!isNERMatchFound && !notFoundNERs.has(exact) && allSelectorL.length > 0) { // 2nd strategy: if exact NER not found, add all drugname matches, add exact to set for avoding add duplicated all matches 
            //notFoundNERs.add(exact);
            console.log("[INFO] exact NER not found - add all drug occurrances (" + allSelectorL.length + ") for exact: " + exact);
            console.log("prefix: |" + prefix + "|");
            console.log("suffix: " + suffix + "|");
            //selectorL = selectorL.concat(allSelectorL);        
            //allSelectorL = [];            
        } 
        
    }
    return selectorL;    
}


// get xpath in string format for DBMI annotator 
// @input: DOM node
// @output: xpath for the node, return null if xpath contains unwanted tags
function getFormattedXPathFromNode(node) {
    pathStr = "";
    // get xpath from dom node
	pathL = getXPath(node);
    // skip matches in table, script, head, etc
	for (p = 0; p < pathL.length; p++){
        if (pathL[p].match(/(table|script|head|h3|h2)/g)){
            return null;
        }                                       
	    pathStr += "/" + pathL[p];
	}
    // skip matches that not in paragraph - [p] tag
    if (pathStr.indexOf("p[") < 0)
        return null
    else
        return pathStr

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
}
