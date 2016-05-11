
if (typeof annotator === 'undefined') {
    alert("Oops! it looks like you haven't built Annotator. " +
          "Either download a tagged release from GitHub, or build the " +
          "package by running `make`");
} else {
    // DBMIAnnotator with highlight and DDI plugin
    var app = new annotator.App();

    // Plugin UI initialize
    //console.log(config);

    var annType = $('#mp-annotation-tb').attr('name');

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

// update 1) annotation table (claim and data) and  2) mpadder (claim menu)
// @input: annotatio source url
// @input: user email
// @input: annotation type
// @input: the column that data & material table sorting by
// @output: update annotation table and mpadder 

function annoList(sourceURL, email, annType, sortByColumn){

    $.ajax({url: 'http://' + config.annotator.host + "/annotatorstore/search",
            data: {annotationType: "MP", 
                   email: email, 
                   uri: sourceURL.replace(/[\/\\\-\:\.]/g, "")},
            method: 'GET',
            error : function(jqXHR, exception){
                console.log(exception);
            },
            success : function(response){
                // claim menu for mpadder
                claimMenu = "";

                // Claim listbox
                claimListbox = "<select id='mp-claim'>";
                for (i = 0; i < response.total; i++){ // add claim label as options
                    row = response.rows[i];

                    claim = row.argues;                    
                    claimListbox += "<option value='" + claim.label + "'>" + claim.label + "</option>";                        
                    claimMenu += "<li id='" + row.id + "' onclick='showright(),dataEditorLoad(\"dose1\",\"" + row.id + "\");'><a href='#'>" + claim.label + "</a></li>";
                }
                claimListbox += "</select>";

                // Method listbox
                methodListbox = "<select id='mp-claim'><option value='clinical-trial'>Clinical Trial</option></select>";
                // Claim 
                claimPanel = "<table>";
                claimPanel += "<tr><td>" + claimListbox + "</td></tr>";
                claimPanel += "<tr><td>Methods: " + methodListbox + "</td></tr>"
                claimPanel += "<tr><td><button type='button'>Edit claim</button>&nbsp;&nbsp;<button type='button'>View claim</button></td></tr></table>";
                
                // Data & Material 
                dataTable = "<table id='mp-data-tb'><tr><td>No. of Participants</td><td>Object Dose</td><td>Participant Dose</td><td>AUC</td><td>Clearance</td><td>Cmax</td><td>Half-life</td></tr><table>";
                dataPanel = "<button type='button'>add new row for data & material</button><br>" + dataTable;

                // Annotation table
                annTable = "<table id='mp-claim-data-tb'>" +
                    "<tr><td>Claim</td><td>Data & Material</td></tr>";             
                annTable += "<tr><td>" + claimPanel + "</td><td>" + dataPanel + "</td></tr>";   
                annTable += "</table>";

                // update Annotation Table
                $("#mp-annotation-tb").html(annTable);                  

                // update mpadder - claim menu                
                $(".mp-sub-menu-2").html(claimMenu);
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


