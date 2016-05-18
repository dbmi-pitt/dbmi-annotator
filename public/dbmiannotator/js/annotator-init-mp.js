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

function getURLParameter(name) {
    return decodeURIComponent((new RegExp('[?|&]' + name + '=' + '([^&;]+?)(&|#|;|$)').exec(location.search)||[,""])[1].replace(/\+/g, '%20'))||null
}

$(document).ready(function () {
    // splitter for show annotation panel
    $('#splitter').jqxSplitter({ showSplitBar: false, width: $(window).width(), height: $(window).height(), orientation: 'horizontal', panels: [{ size: '100%',min: 200 }, { size: '0%', min: 0}] });

    // MP adder - open/close claim menu
    $(function() {
        $('.mp-menu-btn').hover(function() { 
            $('.mp-main-menu').show(); 
        });
    });
    
    $('.mp-main-menu-2').mouseenter(function(){
        $(this).find('.mp-sub-menu-2').slideDown();
    });
    
    $('.mp-main-menu-2').mouseleave(function(){
        $(this).find('.mp-sub-menu-2').slideUp();
    });
 
});


//show right splitter directly
function showright(){
    //open editor tab before editor is triggered
    var index = $("#tabs-1").index();
    $('#tabs').tabs("option", "active", index);
    $('#splitter').jqxSplitter({
        showSplitBar:false,
        width: $(window).width(),
        height: $(window).height(),
        orientation: 'horizontal', 
        panels: [{size: '80%', min: 200}, {size: '20%', min: 280}]
    });
    $('.editorsection').show();
    $('.btn-success').val("show");
    $('.annotator-editor').show();
    $('.btn-success').css("margin-bottom",270);
    $('.btn-home').css("margin-bottom",270);
    $('#menu').html("&nbsp Collapse");
    
    var w = $(window).width()*0.85;
    $('.annotator-widget').width(w);
}


var getUrlParameter = function getUrlParameter(sParam) {
    var sPageURL = decodeURIComponent(window.location.search.substring(1)),
        sURLVariables = sPageURL.split('&'),
        sParameterName,
        i;

    for (i = 0; i < sURLVariables.length; i++) {
        sParameterName = sURLVariables[i].split('=');

        if (sParameterName[0] === sParam) {
            return sParameterName[1] === undefined ? true : sParameterName[1];
        }
    }
};

//show right splitter by button "btn-success"
  function buttonshowright(){
    
    if($('.btn-success').val()=="hide") {

      $('#splitter').jqxSplitter({
        showSplitBar:false,
        width: $(window).width(),
        height: $(window).height(),
        orientation: 'horizontal', 
        panels: [{size: '80%', min: 200}, {size: '20%', min: 280}]
      });
    
      $('#tabs').tabs("option", "active", 0);
      $('.editorsection').hide();
      $('.btn-success').val("show");
      $('.annotator-editor').show();
      $('.btn-success').css("margin-bottom",270);
      $('.btn-home').css("margin-bottom",270);
      $('#menu').html("&nbsp Collapse");
    }
    else {
      $('#splitter').jqxSplitter({
        showSplitBar:false,
        width: '100%',
        height: $(window).height(),
        orientation: 'horizontal', 
        panels: [{size: '100%', min: 200}, {size: '0%', min: 0}]
      });
      $('.btn-success').val("hide");
      $('.annotator-editor').hide();
      $('.btn-success').css("margin-bottom",0);
      $('.btn-home').css("margin-bottom",0);
      $('#menu').html("&nbsp Menu");
    }
    var w = $(window).width()*0.85;
    $('.annotator-widget').width(w);
    
    
  }

  function showrightbyvalue(){
    
    if($('.btn-success').val()=="hide") {
      var tab = $('#tabs-2').attr('href');
      $('#tabs').tabs('select', tab);
      $('#splitter').jqxSplitter({
        showSplitBar:false,
        width: $(window).width(),
        height: $(window).height(),
        orientation: 'horizontal', 
        panels: [{size: '80%', min: 200}, {size: '20%', min: 280}]
      });
      $('.editorsection').show();
      $('.btn-success').val("show");
      $('.annotator-editor').show();
      $('.btn-success').css("margin-bottom",270);
      $('.btn-home').css("margin-bottom",270);
      $('#menu').html("&nbsp Collapse");
    }
    else {
      $('#splitter').jqxSplitter({
        showSplitBar:false,
        width: '100%',
        height: $(window).height(),
        orientation: 'horizontal', 
        panels: [{size: '100%', min: 200}, {size: '0%', min: 0}]
      });
      $('.btn-success').val("hide");
      $('.annotator-editor').hide();
      $('.btn-success').css("margin-bottom",0);
      $('.btn-home').css("margin-bottom",0);
      $('#menu').html("&nbsp Menu");
    }
    var w = $(window).width()*0.85;
    $('.annotator-widget').width(w);
  }
