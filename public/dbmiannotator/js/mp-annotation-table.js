// update 1) annotation table (claim and data) and  2) mpadder (claim menu)
// @input: annotatio source url
// @output: update annotation table and mpadder 

function updateAnnTable(sourceURL){
    console.log("update annotation table");
    //console.log(userEmails);
    // request all mp annotaitons for current document and user

    $.ajax({url: "http://" + config.apache2.host + ":" + config.apache2.port + "/annotatorstore/search",
            data: {annotationType: "MP", 
                   uri: sourceURL.replace(/[\/\\\-\:\.]/g, "")},
            method: 'GET',
            error : function(jqXHR, exception){
                console.log(exception);
		        console.log(jqXHR);
            },
            success : function(response){

                var selectedAnnsL = [];
                for (var i=0; i < response.total; i++) {
                    var ann = response.rows[i];
                    if (userEmails.has(ann.email)) 
                        selectedAnnsL.push(ann);                          
                }
                
                // ann Id for selected claim, if null, set first claim as default 
                if (currAnnotationId == null || currAnnotationId.trim() == "") { 
                    if (selectedAnnsL.length > 0){
                        currAnnotationId = selectedAnnsL[0].id;
                    }
                }

                updateClaimAndData(selectedAnnsL, currAnnotationId);
            }
           });
}

// initiate annotation when user click annotation import button
// @input: list of annotations have been selected for import 
function initAnnTable(selectedAnnsL) {
    console.log("init ann table");
    console.log(selectedAnnsL);

    //if (selectedAnnsL == null) return null;

    // ann Id for selected claim, if null, set first claim as default 
    if ((currAnnotationId == null || currAnnotationId.trim()) == "" && selectedAnnsL != null) { 
        if (selectedAnnsL.length > 0){
            currAnnotationId = selectedAnnsL[0].id;
        }
    }
    updateClaimAndData(selectedAnnsL, currAnnotationId);
}



// update annotation table by selected annotaionId
// @input: list of mp annotaitons
// @input: annotationId for selected claim
function updateClaimAndData(annotations, annotationId) {

    console.log("ann table updateClaimAndData");
    // console.log(annotations);

    // claim menu for mpadder
    claimMenu = "";
    // data table for selected claim
    dataTable = "";
    // loop all MP annotation to create Claim listbox and menu for adder
    claimListbox = "<select id='mp-editor-claim-list' onChange='changeClaimInAnnoTable();'>";
    // create claim listbox in claim creating dialog
    dialogClaimListbox = "<select id='dialog-claim-options' onChange='changeClaimInDialog();'>";
    
    //only when this user has annotations, these content will be generated
    if (annotations != undefined) {
        // add claim label as options in annotation list and mpadder menu
        for (i = 0; i < annotations.length; i++) { 
          
            annotation = annotations[i];
            //if (annotation.annotationType != "MP") continue;

            var claimIsSelected = "";
            if (annotationId == annotation.id) {
                //set global variable
                currAnnotation = annotation;
                //console.log("mp selected: " + annotation.argues.label);
                claimIsSelected = 'selected="selected"';     
                // cache total number of data & material for current claim
                totalDataNum = annotation.argues.supportsBy.length;  
                //if it is not rejected, show the data table
                if (currAnnotation.rejected == null || currAnnotation.rejected == undefined) {
                    dataTable = createDataTable(annotation); // create data table  
                }            
            }
            
            claim = annotation.argues;                    
            option = "<option value='" + annotation.id + "' "+claimIsSelected+">" + claim.label + "</option>";                        
            claimListbox += option;
            dialogClaimListbox += option;

            claimMenu += "<li onclick='claimSelectedInMenu(\""+annotation.id+"\");' ><a href='#'>" + claim.label + "</a></li>";
        }
        claimListbox += "</select>";
        dialogClaimListbox += "</select>";
    }
        // Method listbox
        methodListbox = "<select id='mp-editor-method'><option value='clinical-trial'>Clinical Trial</option></select>";
        // Claim 
        claimPanel = "<table id='mp-claim-method-tb'>";
        claimPanel += "<tr><td>" + claimListbox + "</td></tr>";
        claimPanel += "<tr><td>Methods: " + methodListbox + "</td></tr>";
        
        claimPanel += "<tr><td><button id='edit-claim-btn' type='button' onclick='editClaim()' style='float:left; font-size:12px'>Edit Claim</button><button id='view-claim-btn' type='button' onclick='viewClaim()' style='float: right; font-size:12px'>View Claim</button></td></tr></table>";
        
        var dataPanel = "";
        if (currAnnotation == undefined || currAnnotation.rejected == null || currAnnotation.rejected == undefined) {
            // Data & Material - add new data button 
            dataPanel = "<button id='add-new-data-row-btn' type='button' onclick='addNewDataRow()' style='float: right; font-size:12px'>add new data & material</button>" + dataTable;
        }

    // Annotation table
    annTable = "<table id='mp-claim-data-tb'>" +
        "<tr><td style='width:310px;'>Claim</td><td>Material/Data <strong id='wait' style='display:none;'>Loading...</strong></td></tr>";             
    annTable += "<tr><td>" + claimPanel + "</td><td>" + dataPanel + "</td></tr>";   
    annTable += "</table>";
    
    // update Annotation Table
    $( "#mp-annotation-tb" ).html(annTable);                  
    
    // update mpadder - claim menu                
    $( ".mp-sub-menu-2" ).html(claimMenu);

    // update claim options in dialog
    $( "#dialog-claim-options" ).html(dialogClaimListbox);

    if (annotations == null || annotations.length <= 0) {
        $('#edit-claim-btn').hide();                        
        $('#view-claim-btn').hide();
        $('#mp-editor-method').hide();
        $('#add-new-data-row-btn').hide();
        $('#mp-editor-claim-list').hide();
    } else {
        $('#edit-claim-btn').show();
        $('#view-claim-btn').show();
        $('#mp-editor-method').show();
        $('#add-new-data-row-btn').show();
        $('#mp-editor-claim-list').show();
    }
}

// append new row of data & material in annotation table
function addNewDataRow() {

    var rowCount = $('#mp-data-tb tr').length;
    // set maximum number of rows as 3
    if (rowCount > 3)
        return;

    rowtext = "";
    $('#mp-data-tb tr:last td').map(function() {
        rowtext += $(this).text();
    })

    if (rowtext.trim() == "") {
        return;
    } else {
        totalDataNum += 1;
        dataNumLast = totalDataNum - 1;
       
        $('#mp-data-tb tr:last').after("<tr style='height:20px;'><td onclick='addDataCellByEditor(\"evRelationship\"," + dataNumLast + ", true);'></td><td onclick='addDataCellByEditor(\"participants\"," + dataNumLast + ", true);'> </td><td onclick='addDataCellByEditor(\"dose1\"," + dataNumLast + ", true);'> </td><td onclick='addDataCellByEditor(\"dose2\"," + dataNumLast + ", true);'></td><td onclick='addDataCellByEditor(\"auc\"," + dataNumLast + ", true);'></td><td onclick='addDataCellByEditor(\"cmax\"," + dataNumLast + ", true);'></td><td onclick='addDataCellByEditor(\"clearance\"," + dataNumLast + ", true);'></td><td onclick='addDataCellByEditor(\"halflife\"," + dataNumLast + ", true);'><td onclick='addDataCellByEditor(\"studytype\"," + dataNumLast + ", true);'></td></tr>");
    }
}



// @input: data list in MP annotation
// @input: MP annotation Id
// return: table html for multiple data & materials 
function createDataTable(annotation){

    drugname1 = annotation.argues.qualifiedBy.drug1;
    drugname2 = annotation.argues.qualifiedBy.drug2;
    if (annotation.argues.qualifiedBy.relationship == "interact with") {
        if (annotation.argues.qualifiedBy.precipitant == "drug1")
            drugname1 += " (precipitant)";
        else if (annotation.argues.qualifiedBy.precipitant == "drug2")
            drugname2 += " (precipitant)";
    }
    if (drugname2 == "") {
        dataTable = "<table id='mp-data-tb'><tr><td>Ev Relationship</td><td>No. of Participants</td><td><div>" + drugname1 + " Dose</div></td><td>Phenotype</td><td>AUC ratio</td><td>Cmax ratio</td><td>Clearance ratio</td><td>Half-life ratio</td><td>Study type</td></tr>";
    } else {
        dataTable = "<table id='mp-data-tb'><tr><td>Ev Relationship</td><td>No. of Participants</td><td><div>" + drugname1 + " Dose</div></td><td>" + drugname2 + " Dose</td><td>AUC ratio</td><td>Cmax ratio</td><td>Clearance ratio</td><td>Half-life ratio</td><td>Study type</td></tr>";
    }
    

    annotationId = annotation.id;
    dataL = annotation.argues.supportsBy;

    if (dataL.length > 0){ // show all data items
        for (var dataNum = 0; dataNum < dataL.length; dataNum++) {
            data = dataL[dataNum];
            method = data.supportsBy;
            material = data.supportsBy.supportsBy;
            row = "<tr style='height:20px;'>";
            // evidence relationship
            if (data.evRelationship != null)
                row += "<td onclick='editDataCellByEditor(\"evRelationship\",\""+dataNum+"\");'>" + data.evRelationship + "</td>";      
            else 
                row += "<td onclick='addDataCellByEditor(\"evRelationship\",\""+dataNum+"\");'></td>";

            // show mp material
            if (material.participants.value != null)
                row += "<td onclick='editDataCellByEditor(\"participants\",\""+dataNum+"\");'>" + material.participants.value + "</td>";      
            else 
                row += "<td onclick='addDataCellByEditor(\"participants\",\""+dataNum+"\");'></td>";

            if (material.drug1Dose.value != null)    
                row += "<td onclick='editDataCellByEditor(\"dose1\",\""+dataNum+"\");'>" + material.drug1Dose.value + "</td>";
            else 
                row += "<td onclick='addDataCellByEditor(\"dose1\",\""+dataNum+"\");'></td>"; 

            if (drugname2 == "") {
                console.log("drugname2");
                console.log(drugname2);
                if (material.phenotype != null)
                    row += "<td onclick='editDataCellByEditor(\"phenotype\",\""+dataNum+"\");'>" + material.phenotype.type + "</td>";
                else 
                    row += "<td onclick='addDataCellByEditor(\"phenotype\",\""+dataNum+"\");'></td>";
            } else {
                if (material.drug2Dose.value != null)
                    row += "<td onclick='editDataCellByEditor(\"dose2\",\""+dataNum+"\");'>" + material.drug2Dose.value + "</td>";
                else 
                    row += "<td onclick='addDataCellByEditor(\"dose2\",\""+dataNum+"\");'></td>"; 
            }
            // show mp data
            if (data.auc.value != null)
                row += "<td onclick='editDataCellByEditor(\"auc\",\""+dataNum+"\");'>" + data.auc.value + "</td>";
            else 
                row += "<td onclick='addDataCellByEditor(\"auc\",\""+dataNum+"\");'></td>"; 

            if (data.cmax.value != null)
                row += "<td onclick='editDataCellByEditor(\"cmax\",\""+dataNum+"\");'>" + data.cmax.value + "</td>";
            else 
                row += "<td onclick='addDataCellByEditor(\"cmax\",\""+dataNum+"\");'></td>"; 

            if (data.clearance.value != null)
                row += "<td onclick='editDataCellByEditor(\"clearance\",\""+dataNum+"\");'>" + data.clearance.value + "</td>";
            else 
                row += "<td onclick='addDataCellByEditor(\"clearance\",\""+dataNum+"\");'></td>"; 

            if (data.halflife.value != null)
                row += "<td onclick='editDataCellByEditor(\"halflife\",\""+dataNum+"\");'>" + data.halflife.value + "</td>";
            else 
                row += "<td onclick='addDataCellByEditor(\"halflife\",\""+dataNum+"\");'></td>"; 

            if (data.grouprandom != null || data.parallelgroup != null)
                row += "<td onclick='editDataCellByEditor(\"studytype\",\""+dataNum+"\");'>checked</td>";
            else 
                row += "<td onclick='addDataCellByEditor(\"studytype\",\""+dataNum+"\");'></td>"; 

            row += "</tr>";
            dataTable += row;
        }
    } else { // add empty row
        if (drugname2 == "") {
            dataTable += "<tr style='height:20px;'><td onclick='addDataCellByEditor(\"evRelationship\",0);'></td><td onclick='addDataCellByEditor(\"participants\",0);'></td><td onclick='addDataCellByEditor(\"dose1\",0);'> </td><td onclick='addDataCellByEditor(\"phenotype\",0);'></td><td onclick='addDataCellByEditor(\"auc\",0);'></td><td onclick='addDataCellByEditor(\"cmax\",0);'></td><td onclick='addDataCellByEditor(\"clearance\",0);'></td><td onclick='addDataCellByEditor(\"halflife\",0);'></td><td onclick='addDataCellByEditor(\"studytype\",0);'></td>";
        } else {
            dataTable += "<tr style='height:20px;'><td onclick='addDataCellByEditor(\"evRelationship\",0);'></td><td onclick='addDataCellByEditor(\"participants\",0);'></td><td onclick='addDataCellByEditor(\"dose1\",0);'> </td><td onclick='addDataCellByEditor(\"dose2\",0);'></td><td onclick='addDataCellByEditor(\"auc\",0);'></td><td onclick='addDataCellByEditor(\"cmax\",0);'></td><td onclick='addDataCellByEditor(\"clearance\",0);'></td><td onclick='addDataCellByEditor(\"halflife\",0);'></td><td onclick='addDataCellByEditor(\"studytype\",0);'></td>";
    }   }
    dataTable += "</table>";
    return dataTable;
}


// changed claim in annotation table, update data & material
function changeClaimInAnnoTable() {
    console.log("changeClaimInAnnoTable called");

    var idFromAnnTable = $('#mp-editor-claim-list option:selected').val();

    var idFromDialog = $('#dialog-claim-options option:selected').val();
    var newAnnotationId = idFromAnnTable;

    // update selection in dialog
    if (idFromDialog != newAnnotationId) {
        $("#dialog-claim-options > option").each(function () {
            if (this.value === newAnnotationId) $(this).prop('selected', true);
        });    
    }

    currAnnotationId = newAnnotationId;
    sourceURL = getURLParameter("sourceURL").trim();
    updateAnnTable(sourceURL);
}


// changed claim in annotation table, update data & material
function changeClaimInDialog() {
    var idFromAnnTable = $('#mp-editor-claim-list option:selected').val();
    var idFromDialog = $('#dialog-claim-options option:selected').val();
    var newAnnotationId = idFromDialog;

    // update selection in annotation table
    if (idFromAnnTable != newAnnotationId) 
        $("#mp-editor-claim-list > option").each(function () {
            if (this.value === newAnnotationId) $(this).prop('selected', true);
        });    

    //console.log("dialog - claim changed to :" + newAnnotationId);
    currAnnotationId = newAnnotationId;

    sourceURL = getURLParameter("sourceURL").trim();
    email = getURLParameter("email");

    $.ajax({url: "http://" + config.apache2.host + ":" + config.apache2.port + "/annotatorstore/search",
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
    $("#dialog-select-text-for-data").show();
    $("#select-text-dialog-close").click(function() {
        $("#dialog-select-text-for-data").hide();
    });
}
