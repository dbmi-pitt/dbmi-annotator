// IMPORT
var fs = require('fs'), path = require("path");
var xpath = require('xpath'), parse5 = require('parse5'), xmlser = require('xmlserializer'), dom = require('xmldom').DOMParser;
var Set = require("collections/set");
var HashMap = require('hashmap');
var Q = require('q');
var Promise = require('promise');

// SET VARS
var MIN_TXT = 50; 
var LABEL_HTML_DIR = "Dailymed-SPLs-html/";
var NER_XML_DIR = "NER-results-xml/";

var label1 = "./Dailymed-SPLs-html/test.html"
//var label1 = './Dailymed-SPLs-html/08320ea3-8f93-6f04-5d1c-f69af3eb5a81.html'



parseNERDIR(NER_XML_DIR);
var fs_stat = Q.denodeify(fs.stat)


// PARSE NER XMLS
// @INPUT: dir to NER
// @INPUT: hashmap obj
// @RETURN: NULL
function parseNERDIR(dir){

    var fs_readdir = Q.denodeify(fs.readdir);
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
            
            for (var i = 0; i < files.length; i++ ) {

                var filename = files[i];
                (function(filename){

                    var filepath = NER_XML_DIR + filename;
	                fs.readFile(filepath, 'utf-8', function(error, data){

                        if (error){
                            console.log("Error: ", error);
                        } else {

                            drugL = parseNameInData(data);
                            setid = filename.replace("-drugInteractions.txt-PROCESSED.xml","").replace("-clinicalPharmacology.txt-PROCESSED.xml","");
                            label = LABEL_HTML_DIR+ setid + ".html";
                            
                            //console.log(label);
                            //console.log(drugL[0]);

                            //var data = fs.readFileSync(label, 'utf-8');
                            var rangesL = findDrugInLabel(drugL[0],label);
                            
                            console.log(rangesL[0]);
                            
                        }

	                });
                })(filename)                
            }

        })
}

// PARSE DRUG NAMES IN XML CONTENTS
// @INPUT: XML STRING
// @RETURN: LIST OF UNIQUE DRUG NAMES
var parseNameInData = function(data){ 

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
        return nameS.toArray();
	}
}



// PARSE DRUG OCCURRENCES IN LABEL
// @INPUT: drug name : String
// @INPUT: context : File with path
// @RETURN: List of Ranges {startOffset, endOffset, start, end}

var findDrugInLabel = function(drug, file){

    if (drug == null || file == null) return null;

    var label = fs.readFileSync(file, 'utf-8');
    
    doc = new dom().parseFromString(label);
    drugMatchPattern = "//*[contains(text()[not(name()='script')],'" + drug + "')]";
    
    var drugNodes = xpath.select(drugMatchPattern, doc);
    var rangesL = [];

    for (i = 0; i < drugNodes.length; i++){

	    cntStr = drugNodes[i].firstChild.data;
	    pathL = getXPath(drugNodes[i]);

        if (cntStr){
        
	        if (cntStr.length > MIN_TXT){
                
	            pathStr = ""; 
	            for (j = 0; j < pathL.length; j++){
	    	        pathStr += "/" + pathL[j];
	            }
                
	            var re = new RegExp(drug,"gi");
	            while (res = re.exec(cntStr)){
		            startOffset = res["index"];
		            var ranges = {"label": file,"drugname":drug, "startOffset":startOffset, "endOffset": startOffset + drug.length, "start":pathStr, "end":pathStr};
		            rangesL.push(ranges);
	            }
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




