// IMPORT
var fs = require('fs'), path = require("path");
var xpath = require('xpath'), parse5 = require('parse5'), xmlser = require('xmlserializer'), dom = require('xmldom').DOMParser;
var Set = require("collections/set");
var HashMap = require('hashmap');
var q = require('q');
var Promise = require('promise');

// SET VARS
var MIN_TXT = 50; 
var LABEL_HTML_DIR = "Dailymed-SPLs-html/";
var NER_XML_DIR = "NER-results-xml/";

var label1 = "./Dailymed-SPLs-html/test.html"
//var label1 = './Dailymed-SPLs-html/08320ea3-8f93-6f04-5d1c-f69af3eb5a81.html'


var nerResultsM = new HashMap();
parseNERDIR(NER_XML_DIR, nerResultsM);


// PARSE NER XMLS
// @INPUT: dir to NER
// @INPUT: hashmap obj
// @RETURN: NULL
function parseNERDIR(dir, nerResultsM){
    
    //var nerResultsM = new HashMap();
    
    fs.readdir(dir, function(err, files){
	if (err) throw err;

	for (i = 0; i < files.length; i++){

	    file = dir + files[i];

	    if (path.extname(file) == ".xml"){
		fs.readFile(file, 'utf-8', function(err, data){
	
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

			// nerResultsM.set(file, nameS.toArray());
			// console.log(file);
			// console.log(nerResultsM.get(file));

			// parseDrugInLabel(file + ".xml");
		    }
		});

	    }
	}
	//console.log("test");
    });
   
}


// PARSE LABEL
var parseDrugInLabel = function(file){
    
    fs.readFile(file, {encoding: 'utf-8'}, function (err, data) {
	if (err) throw err;
	
	//var drugStr = "paroxetine";
	var drugStr = "antidepressants";
	findDrugInLabel(drugStr, data);
	//console.log(findDrugInLabel(drugStr, data));
	
    });
}

// PARSE DRUG OCCURRENCES IN LABEL
// @INPUT: drug name : String
// @INPUT: context : String
// @RETURN: List of Ranges {startOffset, endOffset, start, end}

var findDrugInLabel = function(drug, label){

    if (drug == null || label == null) return null;
    
    doc = new dom().parseFromString(label);
    drugMatchPattern = "//*[contains(text()[not(name()='script')],'" + drug + "')]";
    
    var drugNodes = xpath.select(drugMatchPattern, doc);
    var rangesL = [];
    
    for (i = 0; i < drugNodes.length; i++){

	cntStr = drugNodes[i].firstChild.data;
	pathL = getXPath(drugNodes[i]);

	if (cntStr.length > MIN_TXT){

	    pathStr = ""; 
	    for (j = 0; j < pathL.length; j++){
	    	pathStr += "/" + pathL[j];
	    }

	    var re = new RegExp(drug,"gi");
	    while (res = re.exec(cntStr)){
		startOffset = res["index"];
		var ranges = {"startOffset":startOffset, "endOffset": startOffset + drug.length, "start":pathStr, "end":pathStr};
		rangesL.push(ranges);
	    }
	}
    }
    return rangesL;
};


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
      path.push(node.nodeName.toLowerCase() + (node.id ? "[@id='"+node.id+"']" : count > 0 ? "["+count+"]" : ''));
    }
    return path;
  };




