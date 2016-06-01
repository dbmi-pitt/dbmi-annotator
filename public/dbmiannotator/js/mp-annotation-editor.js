// MP CLAIM ================================================================================
// open claim editor
function claimEditorLoad() {
    $("#mp-editor-type").html('claim');
    $("#mp-claim-form").show();
    $(".annotator-save").hide();
    $("#mp-data-nav").hide();
    $("#mp-data-form-participants").hide();
    $("#mp-data-form-dose1").hide();
    $("#mp-data-form-dose2").hide();
    $("#mp-data-form-auc").hide();
    $("#mp-data-form-cmax").hide();
    $("#mp-data-form-cl").hide();
    $("#mp-data-form-halflife").hide();

}

// scroll to the claim text span
function viewClaim() {
    annotationId = $('#mp-editor-claim-list option:selected').val();
    if (document.getElementById(annotationId + "claim")) 
        document.getElementById(annotationId + "claim").scrollIntoView(true);
}

// edit claim
function editClaim() {
    annotationId = $('#mp-editor-claim-list option:selected').val();

    if (document.getElementById(annotationId + "claim")) {
        document.getElementById(annotationId + "claim").scrollIntoView(true);

        showEditor();
        claimEditorLoad();
        
        $.ajax({url: "http://" + config.annotator.host + "/annotatorstore/annotations/" + annotationId,
                data: {},
                method: 'GET',
                error : function(jqXHR, exception){
                    console.log(exception);
                },
                success : function(annotation){
                    // enable delete button
                    $("#annotator-delete").show();
                    
                    // call AnnotatorJs editor for update    
                    app.annotations.update(annotation);   
                }
               });        
    }
}

$("#Drug1").change(function (){selectDrug();});
$("#Drug2").change(function (){selectDrug();});

function selectDrug() {
    var drug1 = $("#Drug1").val();
    var drug2 = $("#Drug2").val();
    var quotestring = $("#quote").html();
    quotestring = quotestring.replace(drug2, "<span class='selecteddrug'>"+drug2+"</span>");
    quotestring = quotestring.replace(drug1, "<span class='selecteddrug'>"+drug1+"</span>");
    $("#quote").html(quotestring);
}

$("#Drug1").mousedown(function (){deselectDrug();});
$("#Drug2").mousedown(function (){deselectDrug();});

function deselectDrug() {
    var drug1 = $("#Drug1").val();
    var drug2 = $("#Drug2").val();
    var quotestring = $("#quote").html();
    quotestring = quotestring.replace("<span class='selecteddrug'>"+drug2+"</span>", drug2);
    quotestring = quotestring.replace("<span class='selecteddrug'>"+drug1+"</span>", drug1);
    $("#quote").html(quotestring);
}


// when relationship is inhibits or substrate of, show field enzyme
function showEnzyme() {

    if($("#relationship option:selected").text()=="inhibits"||$("#relationship option:selected").text()=="substrate of") {
        $("#enzyme")[0].selectedIndex = 0;
        $("#enzymesection1").show();
        $("#enzyme").show();
    }
    if($("#relationship option:selected").text()=="interact with") {
        $("#enzymesection1").hide();
        $("#enzyme").hide();
    }
}


// editor click save and close button
function postEditorSaveAndClose() {

    if ($("#mp-editor-type").html() == "claim") { 
        $( "#claim-dialog-confirm" ).dialog({
            resizable: false,
            height: 'auto',
            width: '400px',
            modal: true,
            buttons: {
                "Add another claim (not ready)": function() {
                    $( this ).dialog( "close" );
                    showrightbyvalue();
                },
                "Add data (not ready)": function() {
                    $( this ).dialog( "close" );
                    showrightbyvalue();
                },
                "Done": function() {
                    $( this ).dialog( "close" );
                    //showAnnTable();
                }
            }
        });
    }

    showAnnTable();    
}

// function dialogDeleteClaim(){

// }


// editor click delete button
function postEditorDelete() {

    if ($("#mp-editor-type").html() == "claim") { 
        $( "#dialog-claim-delete-confirm" ).dialog({
            resizable: false,
            height: 'auto',
            width: '400px',
            modal: true,
            buttons: {
                "confirm": function() {
                    $( this ).dialog( "close" );
                    //showrightbyvalue();
                },
                "cancel": function() {
                    $( this ).dialog( "close" );
                    //showrightbyvalue();
                }
            }
        });
    }

    showAnnTable();    
}



// modify annotaiton id when user pick claim on mpadder's menu
// update annotation table if necessary
function claimSelectedInMenu(annotationId) {
    $("#mp-annotation-work-on").html(annotationId);
    annTableId = $('#mp-editor-claim-list option:selected').val();

    if (annotationId != annTableId){
        $("#mp-editor-claim-list option[value='" + annotationId + "']").attr("selected", "true");
        changeClaimInAnnoTable();
    }
}

// MP DATA & MATERIAL ========================================================================
// open data Editor (1) if annotation is null, then switch form for data field
// (2) otherwise, load annotation to editor, then shown specific form
function dataEditorLoad(annotation, field, annotationId) {
    console.log("dataEditorLoad - id: " + annotationId + " | field: " + field);
    $(".annotator-save").show();
    //$("#annotator-delete").hide();

    // updating current MP annotation
    if (annotationId != null)
        $("#mp-annotation-work-on").html(annotationId);

    switchDataForm(field);

    // show delete button
    material = annotation.argues.supportsBy[0].supportsBy.supportsBy;
    // if (field == "participants" && material.participants.value != null)
    //     $("#annotator-delete").show();
    // else if (field == "dose1" && material.drug1Dose.value != null)
    //     $("#annotator-delete").show();
    // else if (field == "dose2" && material.drug2Dose.value != null)    
    //     $("#annotator-delete").show();

    // call AnnotatorJs editor for update    
    app.annotations.update(annotation);                        
}

// Data editor save, keep form open
function postEditorSave(){
    showEditor();
}

// load data Editor based on selection from annotation table
// (1) if annotation is null, then switch form for data field
// (2) otherwise, load annotation to editor, then shown specific form
function dataEditorLoadAnnTable(field) {

    $(".annotator-save").show();
    //$("#annotator-delete").hide();

    var annotationId = $('#mp-editor-claim-list option:selected').val();
    console.log("dataEditorLoad - id: " + annotationId + " | field: " + field)
    // scroll to the position of annotation

    if (document.getElementById(annotationId + field)) {
        document.getElementById(annotationId + field).scrollIntoView(true);
        
        $.ajax({url: "http://" + config.annotator.host + "/annotatorstore/annotations/" + annotationId,
                data: {},
                method: 'GET',
                error : function(jqXHR, exception){
                    console.log(exception);
                },
                success : function(annotation){

                    // console.log(annotation);
                    // updating current MP annotation
                    if (annotationId != null)
                        $("#mp-annotation-work-on").html(annotationId);
                    
                    switchDataForm(field);

                    // show delete button
                    material = annotation.argues.supportsBy[0].supportsBy.supportsBy;
                    if (field == "participants" && material.participants.value != null)
                        $("#annotator-delete").show();
                    else if (field == "dose1" && material.drug1Dose.value != null)
                        $("#annotator-delete").show();
                    else if (field == "dose2" && material.drug2Dose.value != null) 
                        $("#annotator-delete").show();
                    
                    // call AnnotatorJs editor for update    
                    app.annotations.update(annotation);   
                }
               });            
    }         
}




// open data editor with specific form
function switchDataForm(field) {

    fieldL = ["participants","dose1","dose2","auc","cmax","cl","halflife"];
    
    if (field == null) 
        field = "participants";
    $("#mp-editor-type").html(field);
    
    $("#mp-data-nav").show();
    $("#mp-claim-form").hide();

    // shown specific data form, hide others
    for (i = 0; i < fieldL.length; i++){
        var dataid = "mp-data-form-"+fieldL[i];
        if (fieldL[i] == field){
            $("#"+dataid).show();
        } else {
            $("#"+dataid).hide();
        }
    }
}


