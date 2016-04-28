
if (typeof annotator === 'undefined') {
    alert("Oops! it looks like you haven't built Annotator. " +
          "Either download a tagged release from GitHub, or build the " +
          "package by running `make`");
} else {
    // DBMIAnnotator with highlight and DDI plugin
    var app = new annotator.App();

    // Plugin UI initialize

    console.log(config);

    //var annType = config.profile.def;    

    var annType = $('#annotation-list').attr('name');

    console.log("ddi-plugin.js - annType: " + annType);

    if (annType == "DDI")
        app.include(annotator.ui.dbmimain);            
    else if (annType == "MP")
        app.include(annotator.ui.mpmain);
    else 
        alert("[ERROR] plugin settings wrong, neither DDI nor MP plugin!");

    
    app.include(annotator.storage.debug);
    app.include(annotator.identity.simple);
    app.include(annotator.authz.acl);

    app.include(annotator.storage.http, {
	    prefix: 'http://' + config.store.host + ':' + config.store.port
    });

    var sourceURL = getURLParameter("sourceURL").trim();
    var email = getURLParameter("email");

    var annotationCreateHelper = function () {

	    source = getURLParameter("sourceURL").trim();
    	return {
            beforeAnnotationCreated: function (ann) {
		        ann.rawurl = source;
    		    ann.uri = source.replace(/[\/\\\-\:\.]/g, "");		
		        ann.email = email;
            },
            annotationCreated: function (ann) {
                annoList(ann.rawurl, ann.email, annType);
            },
            annotationUpdated: function(ann) {
                annoList(ann.rawurl, ann.email, annType);
            },
            annotationDeleted: function (ann) {
                setTimeout(function(){
                    annoList(source, email, annType);
                },800);
            }
            
    	};
    };
    app.include(annotationCreateHelper);

    // load annotation after page contents loaded
    app.start().then(function () 
		             {
			             app.ident.identity = email;
			             $(".btn-success").css("display","block");
		             }).then(function(){
			             setTimeout(function(){
			                 app.annotations.load({uri: sourceURL.replace(/[\/\\\-\:\.]/g, ""), email: email});
			             }, 1000);
		             }).then(function(){
                         annoList(sourceURL, email, annType);
                     });
}


function annoList(sourceURL, email, annType, sortByColumn){

    console.log("annType:" + annType);

    $.ajax({url: 'http://' + config.annotator.host + "/annotatorstore/search",
            data: {annotationType: annType, 
                   email: email, 
                   uri: sourceURL.replace(/[\/\\\-\:\.]/g, "")},
            method: 'GET',
            error : function(jqXHR, exception){
                console.log(exception);
            },
            success : function(response){

                if (response.total > 0){

                    fieldsL = ["Drug1", "relationship", "Drug2", "assertion_type", "updated"];
                    if (sortByColumn != null){
                        sort(response.rows, sortByColumn);
                    }

                    listTable = "<table id='tb-annotation-list'><tr>" +
"<td><div id=fields[0] class='tb-list-unsorted' onclick='annoList(sourceURL, email, annType, fieldsL[0])'>Subject</div></td>" +
"<td><div id=fields[1] class='tb-list-unsorted' onclick='annoList(sourceURL, email, annType, fieldsL[1])'>Predicate</div></td>" +
"<td><div id=fields[2] class='tb-list-unsorted' onclick='annoList(sourceURL, email, annType, fieldsL[2])'>Object</div></td>" +
"<td><div id=fields[3] class='tb-list-unsorted' onclick='annoList(sourceURL, email, annType, fieldsL[3])'>Assertion Type</div></td>" +
"<td><div id=fields[4] class='tb-list-unsorted' onclick='annoList(sourceURL, email,  annType, fieldsL[4])'>Date</div></td><td>Text quote</td></tr>";

                    for (i = 0; i < response.total; i++){
                        row = response.rows[i];
                        quote = row.target.selector.exact;
                        if (quote.length > 65){
                            quote = quote.substring(0, 65) + "...";
                        }
                        
                        date = new Date(row.updated);
                        dateUpdated = [date.toDateString(), date.toLocaleTimeString()].join(' ');                    
                        listTable += "<tr><td>" + row.Drug1 + "</td><td>" + row.relationship + "</td><td>" + row.Drug2 + "</td><td>" + row.assertion_type + "</td><td>" + dateUpdated + "</td><td><a href='#" + row.id + "'>" + quote + "</a></td></tr>"
                    }
                    listTable += "</table>";
                    $("#annotation-list").html(listTable);  
                } else {
                    $("#annotation-list").html("No DDI annotations been made!");  
                }
                
            }
     
           });
}


function sort(annotations, sortByColumn) {

    //console.log("sortByColumn: " + sortByColumn);
    // console.log($("#tb-annotation-list"));
    // className = $("#tb-annotation-list").find('#' + sortByColumn).attr('class');
    // console.log("className: " + className);

    // if (className == "tb-list-unsorted"){
        
    //     $('#' + sortByColumn).attr('class','tb-list-asc');
    //     annotations.sort(function(a, b){
    //         return a[sortByColumn].localeCompare(b[sortByColumn]);
    //     });
    // } else if (className == "tb-list-asc"){
    //     annotations.sort(function(a, b){
    //         return a[sortByColumn].localeCompare(b[sortByColumn]);
    //     }).reverse();
    // }

    $('#' + sortByColumn).attr('class','tb-list-asc');
        annotations.sort(function(a, b){
            return a[sortByColumn].localeCompare(b[sortByColumn]);
        });
}



function getURLParameter(name) {
    return decodeURIComponent((new RegExp('[?|&]' + name + '=' + '([^&;]+?)(&|#|;|$)').exec(location.search)||[,""])[1].replace(/\+/g, '%20'))||null
}


