// MP CLAIM ================================================================================
// open claim editor
function claimEditorLoad() {
    $("#mp-editor-type").html('claim');
    $("#mp-claim-form").show();
    $(".annotator-save").hide();

    showEnzyme();

    $("#mp-data-nav").hide();
    $("#mp-data-form-participants").hide();
    $("#mp-data-form-dose1").hide();
    $("#mp-data-form-dose2").hide();
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
$("#relationship").change(function showEnzyme() {
    if($("#relationship option:selected").text()=="inhibits"||$("#relationship option:selected").text()=="substrate of") {
        $("#enzymesection1").show();
        $("#enzyme").show();
    }
    if($("#relationship option:selected").text()=="interact with") {
        $("#enzymesection1").hide();
        $("#enzyme").hide();
    }
});


function showEnzyme() {
    if($("#relationship option:selected").text()=="inhibits"||$("#relationship option:selected").text()=="substrate of") {
        $("#enzymesection1").show();
        $("#enzyme").show();
    }
    if($("#relationship option:selected").text()=="interact with") {
        $("#enzymesection1").hide();
        $("#enzyme").hide();
    }
}


// Claim editor submit with options 1) continue create claim, 2) add data, 3) done
// Data editor save, keep form open
function postEditorSave(){

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
                "Add another claim": function() {
                    $( this ).dialog( "close" );
                    showrightbyvalue();
                },
                "Add data": function() {
                    $( this ).dialog( "close" );
                    showrightbyvalue();
                },
                "Done": function() {
                    $( this ).dialog( "close" );
                    showAnnTable();
                }
            }
        });
    } else {
        showAnnTable();
    }
    
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
    // updating current MP annotation
    if (annotationId != null)
        $("#mp-annotation-work-on").html(annotationId);

    switchDataForm(field);

    // call AnnotatorJs editor for update    
    app.annotations.update(annotation);                        
}


// load data Editor based on selection from annotation table
// (1) if annotation is null, then switch form for data field
// (2) otherwise, load annotation to editor, then shown specific form
function dataEditorLoadAnnTable(field) {

    $(".annotator-save").show();
    var annotationId = $('#mp-editor-claim-list option:selected').val();
    console.log("dataEditorLoad - id: " + annotationId + " | field: " + field);

    $.ajax({url: "http://" + config.annotator.host + "/annotatorstore/annotations/" + annotationId,
            data: {},
            method: 'GET',
            error : function(jqXHR, exception){
                console.log(exception);
            },
            success : function(annotation){

                console.log(annotation);
                // updating current MP annotation
                if (annotationId != null)
                    $("#mp-annotation-work-on").html(annotationId);

                switchDataForm(field);

                // call AnnotatorJs editor for update    
                app.annotations.update(annotation);   
            }
           });                     
}




// open data editor with specific form
function switchDataForm(field) {

    fieldL = ["participants","dose1","dose2"];
    
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


