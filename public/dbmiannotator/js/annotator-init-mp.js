
if (typeof annotator === 'undefined') {
    alert("Oops! it looks like you haven't built Annotator. " +
          "Either download a tagged release from GitHub, or build the " +
          "package by running `make`");
} else {
    // DBMIAnnotator with highlight and DDI plugin
    var app = new annotator.App();

    var annType = $('#mp-annotation-tb').attr('name');

    if (annType == "DDI")
        app.include(annotator.ui.dbmimain);            
    else if (annType == "MP")
        app.include(annotator.ui.mpmain, {element: subcontent});
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
                annotationTable(ann.rawurl, ann.email);
            },
            annotationUpdated: function(ann) {
                annotationTable(ann.rawurl, ann.email);
            },
            annotationDeleted: function (ann) {
                setTimeout(function(){
                    annotationTable(source, email);
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
                         annotationTable(sourceURL, email);
                     });
}

// update 1) annotation table (claim and data) and  2) mpadder (claim menu)
// @input: annotatio source url
// @input: user email
// @input: annotation type
// @input: the column that data & material table sorting by
// @output: update annotation table and mpadder 

function annotationTable(sourceURL, email, sortByColumn){

    // request all mp annotaitons for current document and user
    $.ajax({url: "http://" + config.annotator.host + "/annotatorstore/search",
            data: {annotationType: "MP", 
                   email: email, 
                   uri: sourceURL.replace(/[\/\\\-\:\.]/g, "")},
            method: 'GET',
            error : function(jqXHR, exception){
                console.log(exception);
            },
            success : function(response){

                    // ann Id for selected claim, if null, set first claim as default 
                    var annotationId = $("#mp-annotation-work-on").html();    

                    if (annotationId == null || annotationId.trim() == "") {         
                        if (response.total > 0){
                            $("#mp-annotation-work-on").html(response.rows[0].id);
                            annotationId = response.rows[0].id;
                        }
                    }
                    updateClaimAndData(response.rows, annotationId);
            }
           });
}

// update annotation table by selected annotaionId
// @input: list of mp annotaitons
// @input: annotationId for selected claim
function updateClaimAndData(annotations, annotationId) {
    // claim menu for mpadder
    claimMenu = "";
    // data table for selected claim
    dataTable = "";
    // loop all MP annotation to create Claim listbox and menu for adder
    claimListbox = "<select id='mp-editor-claim-list' onChange='changeClaimInAnnoTable();'>";
    // add claim label as options in annotation list and mpadder menu
    for (i = 0; i < annotations.length; i++) { 
        
        annotation = annotations[i];
        dataL = annotation.argues.supportsBy;

        var claimIsSelected = "";
        if (annotationId == annotation.id) {
            console.log("mp selected: " + annotation.argues.label);
            claimIsSelected = 'selected="selected"';           
                
            // create data table
            dataTable = createDataTable(dataL, annotationId);                       
        }
        
        claim = annotation.argues;                    
        claimListbox += "<option value='" + annotation.id + "' "+claimIsSelected+">" + claim.label + "</option>";                        
        claimMenu += "<li onclick='claimSelectedInMenu(\""+annotation.id+"\");' ><a href='#'>" + claim.label + "</a></li>";
    }
    claimListbox += "</select>";
    
    // Method listbox
    methodListbox = "<select id='mp-editor-method'><option value='clinical-trial'>Clinical Trial</option></select>";
    // Claim 
    claimPanel = "<table>";
    claimPanel += "<tr><td>" + claimListbox + "</td></tr>";
    claimPanel += "<tr><td>Methods: " + methodListbox + "</td></tr>"
    claimPanel += "<tr><td><button type='button'>Edit claim</button>&nbsp;&nbsp;<button type='button'>View claim</button></td></tr></table>";
    
    // Data & Material 
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



// @input: data list in MP annotation
// @input: MP annotation Id
// return: table html for multiple data & materials 
function createDataTable(dataL, annotationId){
    console.log(annotationId);

    dataTable = "<table id='mp-data-tb'><tr><td>No. of Participants</td><td>Drug1 Dose</td><td>Drug2 Dose</td><td>AUC</td><td>Clearance</td><td>Cmax</td><td>Half-life</td></tr>";

    if (dataL.length > 0){
        for (j = 0; j < dataL.length; j++){
            data = dataL[j];
            method = data.supportsBy;
            material = data.supportsBy.supportsBy;
            row = "<tr>";
            row += "<td onclick='showright(),dataEditorLoadAnnTable(\"participants\");'>" + material.participants.value + "</td>";        
            row += "<td onclick='showright(),dataEditorLoadAnnTable(\"dose1\");'>" + material.drug1Dose.value + "</td>";
            row += "<td onclick='showright(),dataEditorLoadAnnTable(\"dose2\");'>" + material.drug2Dose.value + "</td>";
            row += "<td></td><td></td><td></td><td></td></tr>";
            dataTable += row;
        }
    }
    dataTable += "</table>";
    return dataTable;
}


// sort data & materail table by column 
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
