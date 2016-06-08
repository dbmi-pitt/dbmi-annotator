// update 1) annotation table (claim and data) and  2) mpadder (claim menu)
// @input: annotatio source url
// @input: user email
// @input: annotation type
// @input: the column that data & material table sorting by
// @output: update annotation table and mpadder 

function annotationTable(sourceURL, email, sortByColumn){
    console.log("refresh ann table");
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

        //console.log(annotationId + "| " + annotations[i].id);        
        annotation = annotations[i];
        dataL = annotation.argues.supportsBy;

        var claimIsSelected = "";
        if (annotationId == annotation.id) {
            console.log("mp selected: " + annotation.argues.label);
            claimIsSelected = 'selected="selected"';     
            // cache total number of data & material for current claim
            totalDataNum = dataL.length;      
            
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
    dataPanel = "<button type='button' onclick='addNewDataRow()' style='float: right;'>add new data & material</button><br>" + dataTable;
    
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

// append new row of data & material in annotation table
function addNewDataRow() {
    totalDataNum += 1;
    dataNumLast = totalDataNum - 1;

    $('#mp-data-tb tr:last').after("<tr style='height:20px;'><td onclick='addDataCellByEditor(\"participants\"," + dataNumLast + ", true);'> </td><td onclick='addDataCellByEditor(\"dose1\"," + dataNumLast + ", true);'> </td><td onclick='addDataCellByEditor(\"dose2\"," + dataNumLast + ", true);'></td><td onclick='addDataCellByEditor(\"auc\"," + dataNumLast + ", true);'></td><td onclick='addDataCellByEditor(\"cmax\"," + dataNumLast + ", true);'></td><td onclick='addDataCellByEditor(\"clearance\"," + dataNumLast + ", true);'></td><td onclick='addDataCellByEditor(\"halflife\"," + dataNumLast + ", true);'></td></tr>");
}



// @input: data list in MP annotation
// @input: MP annotation Id
// return: table html for multiple data & materials 
function createDataTable(dataL, annotationId){

    dataTable = "<table id='mp-data-tb'><tr><td>No. of Participants</td><td>Drug1 Dose</td><td>Drug2 Dose</td><td>AUC</td><td>Cmax</td><td>Clearance</td><td>Half-life</td></tr>";

    if (dataL.length > 0){ // show all data items
        for (var dataNum = 0; dataNum < dataL.length; dataNum++) {
            data = dataL[dataNum];
            method = data.supportsBy;
            material = data.supportsBy.supportsBy;
            row = "<tr style='height:20px;'>";
            // show mp material
            if (material.participants.value != null)
                row += "<td onclick='editDataCellByEditor(\"participants\",\""+dataNum+"\");'>" + material.participants.value + "</td>";      
            else 
                row += "<td onclick='addDataCellByEditor(\"participants\",\""+dataNum+"\");'></td>";

            if (material.drug1Dose.value != null)    
                row += "<td onclick='editDataCellByEditor(\"dose1\",\""+dataNum+"\");'>" + material.drug1Dose.value + "</td>";
            else 
                row += "<td onclick='addDataCellByEditor(\"dose1\",\""+dataNum+"\");'></td>"; 

            if (material.drug2Dose.value != null)
                row += "<td onclick='editDataCellByEditor(\"dose2\",\""+dataNum+"\");'>" + material.drug2Dose.value + "</td>";
            else 
                row += "<td onclick='addDataCellByEditor(\"dose2\",\""+dataNum+"\");'></td>"; 
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

            row += "</tr>";
            dataTable += row;
        }
    } else { // add empty row
        dataTable += "<tr style='height:20px;'><td onclick='addDataCellByEditor(\"participants\",0);'> </td><td onclick='addDataCellByEditor(\"dose1\",0);'> </td><td onclick='addDataCellByEditor(\"dose2\",0);'></td><td onclick='addDataCellByEditor(\"auc\",0);'></td><td onclick='addDataCellByEditor(\"cmax\",0);'></td><td onclick='addDataCellByEditor(\"clearance\",0);'></td><td onclick='addDataCellByEditor(\"halflife\",0);'></td></tr>";
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


