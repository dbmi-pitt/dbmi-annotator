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
    method_entered = "";
    
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
                claimIsSelected = 'selected="selected"';     
                method_entered = annotation.argues.method;
                // cache total number of data & material for current claim
                totalDataNum = annotation.argues.supportsBy.length;  
                //if it is not rejected, show the data table

                if (currAnnotation.argues.method == "Case Report") {
                    dataTable = createDipsTable(annotation);                    
                } else if (currAnnotation.argues.method == "statement") {
                    dataTable = createStatTable(annotation);
                } else {
                    dataTable = createDataTable(annotation); // create data table  
                }
                            
                totalDataNum = annotation.argues.supportsBy.length;      
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

    // Claim 
    claimPanel = "<table id='mp-claim-method-tb'>";
    claimPanel += "<tr><td>" + claimListbox + "</td></tr>";

    // Method listbox - user entered method
    claimPanel += "<tr><td>Method: " + method_entered + "</td></tr>"
        
    claimPanel += "<tr><td><button id='edit-claim-btn' type='button' onclick='editClaim()' style='float:left; font-size:12px'>Edit Claim</button><button id='view-claim-btn' type='button' onclick='viewClaim()' style='float: right; font-size:12px'>View Claim</button></td></tr></table>";
        
    // When method is statement, disable adding rows
    var dataPanel = "";

    if (currAnnotation == undefined || (currAnnotation.argues.method != "statement" && currAnnotation.argues.method != "Case Report")) {
        // Data & Material - add new data button 
        dataPanel = "<button id='add-new-data-row-btn' type='button' onclick='addNewDataRow()' style='float: right; font-size:12px'>add new data & material</button>" + dataTable;
    } else if (currAnnotation.argues.method == "statement") {
        dataPanel = dataTable;
    } else if (currAnnotation.argues.method == "Case Report") {
        var dose1 = currAnnotation.argues.supportsBy.length == 0 ? "" : currAnnotation.argues.supportsBy[0].supportsBy.supportsBy.drug1Dose.value;
        var dose2 = currAnnotation.argues.supportsBy.length == 0 ? "" : currAnnotation.argues.supportsBy[0].supportsBy.supportsBy.drug2Dose.value;
        dataPanel = "<button id='add-new-data-row-btn' type='button' onclick='addNewDipsRow("+dose1+","+dose2+")' style='float: right; font-size:12px'>add new data & material</button>" + dataTable;
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

// append new row of dips score in annotation table
function addNewDipsRow(dose1, dose2) {
    var rowCount = $('#mp-dips-tb tr').length;
    // set maximum number of rows as 3
    if (rowCount > 3)
        return;

    rowtext = "";
    $('#mp-dips-tb tr:last td').map(function() {
        rowtext += $(this).text();
    })

    if (rowtext.trim() == "") {
        return;
    } else {
        totalDataNum += 1;
        dataNumLast = totalDataNum - 1;
        var temp = "<tr style='height:20px;'>" + "<td onclick='addDataCellByEditor(\"reviewer\",\""+dataNumLast+"\", true);'></td><td onclick='addDataCellByEditor(\"dose1\",\"" + dataNumLast + "\", true);'>"+(dose1==undefined?"":dose1)+"</td><td onclick='addDataCellByEditor(\"dose2\",\"" + dataNumLast + "\", true);'>"+(dose2==undefined?"":dose2)+"</td>"
        for (var i = 1; i <= 10; i++) {
            //temp += "<td onclick='addDataCellByEditor(\"q"+i+"\",\""+dataNumLast+"\");'></td>";
            temp += "<td><img src='img/cell-uneditorable.png' style='width:20px;height:17px;'></td>";
        }
        temp += "<td>NA</td></tr>";
        $('#mp-dips-tb tr:last').after(temp);
    }
}


// @input: annotation
// return: table html for multiple DIPS score and dosing info
function createDipsTable(annotation){
    //precipitant info
    drugname1 = annotation.argues.qualifiedBy.drug1;
    drugname2 = annotation.argues.qualifiedBy.drug2;
    if (annotation.argues.qualifiedBy.relationship == "interact with") {
        if (annotation.argues.qualifiedBy.precipitant == "drug1")
            drugname1 += " (precipitant)";
        else if (annotation.argues.qualifiedBy.precipitant == "drug2")
            drugname2 += " (precipitant)";
    }
    //reject info
    if (annotation.rejected == undefined || annotation.rejected == null ) {
        dataTable = "<table style='border-color:green;color:green;'";
    } else {
        dataTable = "<table style='color:red;'";
    }

    dataTable += " id='mp-dips-tb'><tr><td>Reviewer</td><td><div>" + drugname1 + " Dose</div></td><td>" + drugname2 + " Dose</td>";
    for (var i = 1; i <= 10; i++) {
        dataTable += "<td><a href='#' title='" + $("#dips-q" + i + "-label").text() + "'>Q" + i + "</a></td>";
    }
    dataTable += "<td>Total</td></tr>"
    dataL = annotation.argues.supportsBy;

    if (dataL.length > 0){ // show all data items
        for (var dataNum = 0; dataNum < dataL.length; dataNum++) {
            data = dataL[dataNum];
            method = data.supportsBy;
            material = data.supportsBy.supportsBy;
            
            var row = "<tr style='height:20px;'>";

            // show reviewer info
            if (data.reviewer.reviewer != null)
                row += "<td onclick='editDataCellByEditor(\"reviewer\",\""+dataNum+"\");'>" + data.reviewer.reviewer + "</td>";      
            else 
                row += "<td onclick='addDataCellByEditor(\"reviewer\",\""+dataNum+"\");'></td>";

            // show dosing info
            if (material.drug1Dose.value != null)    
                row += "<td onclick='editDataCellByEditor(\"dose1\",\""+dataNum+"\");'>" + material.drug1Dose.value + "</td>";
            else 
                row += "<td onclick='addDataCellByEditor(\"dose1\",\""+dataNum+"\");'></td>"; 
            
            if (material.drug2Dose.value != null)
                row += "<td onclick='editDataCellByEditor(\"dose2\",\""+dataNum+"\");'>" + material.drug2Dose.value + "</td>";
            else 
                row += "<td onclick='addDataCellByEditor(\"dose2\",\""+dataNum+"\");'></td>"; 

            // show dips question
            if (data.reviewer.lackInfo) {
                for (var i = 1; i <= 10; i++) {
                    row += "<td><img src='img/cell-uneditorable.png' style='width:20px;height:17px;'></td>"; 
                }
            } else {
                for (var i = 1; i <= 10; i++) {
                    if (data.dips["q" + i] != null) {
                        row += "<td onclick='editDataCellByEditor(\"q"+i+"\",\""+dataNum+"\");'>" + data.dips["q"+i] + "</td>";
                    } else {
                        row += "<td onclick='addDataCellByEditor(\"q"+i+"\",\""+dataNum+"\");'></td>"; 
                    }
                }
            }

            //show dips total score
            if (data.reviewer.total != null)
                row += "<td>" + data.reviewer.total + "</td>";
            else 
                row += "<td>NA</td>"; 

            row += "</tr>";
            dataTable += row;
        }
    } else { // add empty row
        dataTable += "<tr style='height:20px;'><td onclick='addDataCellByEditor(\"reviewer\",0);'></td><td onclick='addDataCellByEditor(\"dose1\",0);'> </td><td onclick='addDataCellByEditor(\"dose2\",0);'></td>";
        for (var i = 1; i <= 10; i++) {
            dataTable += "<td><img src='img/cell-uneditorable.png' style='width:20px;height:17px;'></td>"; 
        }
        dataTable += "<td>NA</td></tr>";
    }
    dataTable += "</table>";
    return dataTable;
}


// @input: data list in MP annotation
// @input: MP annotation Id
// return: table html for multiple data & materials 
function createDataTable(annotation){
    var dataTable;
    drugname1 = annotation.argues.qualifiedBy.drug1;
    drugname2 = annotation.argues.qualifiedBy.drug2;
    if (annotation.argues.qualifiedBy.relationship == "interact with") {
        if (annotation.argues.qualifiedBy.precipitant == "drug1")
            drugname1 += " (precipitant)";
        else if (annotation.argues.qualifiedBy.precipitant == "drug2")
            drugname2 += " (precipitant)";
    }
    if (annotation.rejected == undefined || annotation.rejected == null ) {
        dataTable = "<table style='color:green;'";
    } else {
        dataTable = "<table style='color:red;'";
    }
    if (drugname2 == "") {
        dataTable += " id='mp-data-tb'><tr><td>Ev Relationship</td><td>No. of Participants</td><td><div>" + drugname1 + " Dose</div></td><td>Phenotype</td><td>AUC ratio</td><td>Cmax ratio</td><td>Clearance ratio</td><td>Half-life ratio</td><td>Study type</td></tr>";
    } else {
        dataTable += " id='mp-data-tb'><tr><td>Ev Relationship</td><td>No. of Participants</td><td><div>" + drugname1 + " Dose</div></td><td>" + drugname2 + " Dose</td><td>AUC ratio</td><td>Cmax ratio</td><td>Clearance ratio</td><td>Half-life ratio</td><td>Study type</td></tr>";
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
                if (material.phenotype != null) {
                    row += "<td onclick='editDataCellByEditor(\"phenotype\",\""+dataNum+"\");'>" + material.phenotype.type + "</td>";
                } else {
                    row += "<td onclick='addDataCellByEditor(\"phenotype\",\""+dataNum+"\");'></td>";
                }
                $('#nav-dose2-btn').hide();
                $('nav-phenotype-btn').show();
            } else {
                if (material.drug2Dose.value != null)
                    row += "<td onclick='editDataCellByEditor(\"dose2\",\""+dataNum+"\");'>" + material.drug2Dose.value + "</td>";
                else 
                    row += "<td onclick='addDataCellByEditor(\"dose2\",\""+dataNum+"\");'></td>"; 
                $('#nav-dose2-btn').show();
                $('nav-phenotype-btn').hide();
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

function createStatTable(annotation) {
    negation = annotation.argues.negation;
    dataTable = "<table style='font-size: 13px !important; background-color: white !important;'><tr><td>Negation</td></tr><tr><td>"+negation+"</td></tr></table>";
    return dataTable;
}


// changed claim in annotation table, update data & material
function changeClaimInAnnoTable() {
    console.log("changeClaimInAnnoTable called");

    var idFromAnnTable = $('#mp-editor-claim-list option:selected').val();
    scrollToAnnotation(idFromAnnTable, "claim", 0); // jump to claim

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

// scroll to the claim text span
function viewClaim() {
    annotationId = $('#mp-editor-claim-list option:selected').val();
    scrollToAnnotation(annotationId, "claim", 0);
}
