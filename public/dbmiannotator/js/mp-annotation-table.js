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

        //console.log(annotationId + "| " + annotations[i].id);        
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
    claimPanel = "<table id='mp-claim-method-tb'>";
    claimPanel += "<tr><td>" + claimListbox + "</td></tr>";
    claimPanel += "<tr><td>Methods: " + methodListbox + "</td></tr>"
    claimPanel += "<tr><td><button type='button' onclick='editClaim()'>Edit claim</button>&nbsp;&nbsp;<button type='button' onclick='viewClaim()'>View claim</button></td></tr></table>";
    
    // Data & Material - add new data button 
    dataPanel = "<button type='button' style='float: right;'>add new data & material (not ready)</button><br>" + dataTable;
    dataPanel = dataTable;
    
    // Annotation table
    annTable = "<table id='mp-claim-data-tb'>" +
        "<tr><td>Claim</td><td>Data & Material</td></tr>";             
    annTable += "<tr><td>" + claimPanel + "</td><td>" + dataPanel + "</td></tr>";   
    annTable += "</table>";
    
    // update Annotation Table
    $("#mp-annotation-tb").html(annTable);                  
    
    // update mpadder - claim menu                
    $(".mp-sub-menu-2").html(claimMenu);
    console.log("claim menu updated!");
}



// @input: data list in MP annotation
// @input: MP annotation Id
// return: table html for multiple data & materials 
function createDataTable(dataL, annotationId){

    dataTable = "<table id='mp-data-tb'><tr><td>No. of Participants</td><td>Drug1 Dose</td><td>Drug2 Dose</td><td>AUC</td><td>Clearance</td><td>Cmax</td><td>Half-life</td></tr>";

    if (dataL.length > 0){ // show all data items
        for (j = 0; j < dataL.length; j++) {
            data = dataL[j];
            method = data.supportsBy;
            material = data.supportsBy.supportsBy;
            row = "<tr style='height:20px;'>";
            // show mp material
            if (material.participants.value != null)
                row += "<td onclick='showEditor(),dataEditorLoadAnnTable(\"participants\");'>" + material.participants.value + "</td>";      
            else 
                row += "<td onclick='warnSelectTextSpan(\"participants\");'></td>"; 

            if (material.drug1Dose.value != null)    
                row += "<td onclick='showEditor(),dataEditorLoadAnnTable(\"dose1\");'>" + material.drug1Dose.value + "</td>";
            else 
                row += "<td onclick='warnSelectTextSpan(\"dose1\");'></td>"; 

            if (material.drug2Dose.value != null)
                row += "<td onclick='showEditor(),dataEditorLoadAnnTable(\"dose2\");'>" + material.drug2Dose.value + "</td>";
            else 
                row += "<td onclick='warnSelectTextSpan(\"dose2\");'></td>"; 
            // show mp data
            if (data.auc.value != null)
                row += "<td onclick='showEditor(),dataEditorLoadAnnTable(\"auc\");'>" + data.auc.value + "</td>";
            else 
                row += "<td onclick='warnSelectTextSpan(\"auc\");'></td>"; 

            if (data.cmax.value != null)
                row += "<td onclick='showEditor(),dataEditorLoadAnnTable(\"cmax\");'>" + data.cmax.value + "</td>";
            else 
                row += "<td onclick='warnSelectTextSpan(\"cmax\");'></td>"; 

            if (data.cl.value != null)
                row += "<td onclick='showEditor(),dataEditorLoadAnnTable(\"cl\");'>" + data.cl.value + "</td>";
            else 
                row += "<td onclick='warnSelectTextSpan(\"cl\");'></td>"; 

            if (data.halflife.value != null)
                row += "<td onclick='showEditor(),dataEditorLoadAnnTable(\"halflife\");'>" + data.halflife.value + "</td>";
            else 
                row += "<td onclick='warnSelectTextSpan(\"halflife\");'></td>"; 

            row += "</tr>";
            dataTable += row;
        }
    } else { // add empty row
        dataTable += "<tr style='height:20px;'><td onclick='warnSelectTextSpan(\"participants\");'> </td><td onclick='warnSelectTextSpan(\"dose1\");'> </td><td onclick='warnSelectTextSpan(\"dose2\");'></td><td onclick='warnSelectTextSpan(\"auc\");'></td><td onclick='warnSelectTextSpan(\"cmax\");'></td><td onclick='warnSelectTextSpan(\"cl\");'></td><td onclick='warnSelectTextSpan(\"halflife\");'></td></tr>"
    }
    dataTable += "</table>";
    return dataTable;
}


// changed claim in annotation table, update data & material
function changeClaimInAnnoTable() {
    var newAnnotationId = $('#mp-editor-claim-list option:selected').val();
    console.log("claim changed to :" + newAnnotationId);
    $("#mp-annotation-work-on").html(newAnnotationId);

    sourceURL = getURLParameter("sourceURL").trim();
    email = getURLParameter("email");

    $.ajax({url: "http://" + config.annotator.host + "/annotatorstore/search",
            data: {annotationType: "MP", 
                   email: email, 
                   uri: sourceURL.replace(/[\/\\\-\:\.]/g, "")},
            method: 'GET',
            error : function(jqXHR, exception){
                console.log(exception);
            },
            success : function(response){
                updateClaimAndData(response.rows, newAnnotationId);
            }     
           });    
}

// pop up warning box that user have to select text span for adding data
// set current data field for editor form to the field that user chosen
function warnSelectTextSpan(field) {
    $("#dialog-select-text-for-data").dialog();
    $("#mp-editor-type").html(field);
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


