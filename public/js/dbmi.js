$(document).ready(function () {
    $('#splitter').jqxSplitter({ width: $(window).width(), height: '100%',  panels: [{ size: '100%', min: 100 }, { size: '0%', min: 0}] });
    //$('.secondsection').append("<p><a href='http://www.google.com'>Google</a></p>");
  });

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
        width: $(window).width(),
        height: '100%',
        panels: [{size: '67%', min: 850}, {size: '33%', min: 410}]
      });
      $('.editorsection').hide();
      $('.btn-success').val("show");
      $('.annotator-editor').show();
      $('.btn-success').css("margin-right",425);
    }
    else {
      $('#splitter').jqxSplitter({
        width: '100%',
        height: '100%',
        panels: [{size: '100%', min: 100}, {size: '0%', min: 0}]
      });
      $('.btn-success').val("hide");
      $('.annotator-editor').hide();
      $('.btn-success').css("margin-right",0);
    }
    var w = $(window).width()*0.31;
    $('.annotator-widget').width(w);
    
    
  }

  function showrightbyvalue(){
    
    if($('.btn-success').val()=="hide") {
      var tab = $('#tabs-2').attr('href');
      $('#tabs').tabs('select', tab);
      $('#splitter').jqxSplitter({
        width: $(window).width(),
        height: '100%',
        panels: [{size: '67%', min: 850}, {size: '33%', min: 410}]
      });
      $('.editorsection').show();
      $('.btn-success').val("show");
      $('.annotator-editor').show();
      $('.btn-success').css("margin-right",425);
    }
    else {
      $('#splitter').jqxSplitter({
        width: '100%',
        height: '100%',
        panels: [{size: '100%', min: 100}, {size: '0%', min: 0}]
      });
      $('.btn-success').val("hide");
      $('.annotator-editor').hide();
      $('.btn-success').css("margin-right",0);
    }
    var w = $(window).width()*0.31;
    $('.annotator-widget').width(w);
  }

//show right splitter directly
  function showright(){
      //open editor tab before editot is triggered
      var index = $("#tabs-1").index();
      $('#tabs').tabs("option", "active", index);
      $('#splitter').jqxSplitter({
        width: $(window).width(),
        height: '100%',
        panels: [{size: '67%', min: 850}, {size: '33%', min: 410}]
      });
      $('.editorsection').show();
      $('.btn-success').val("show");
      $('.annotator-editor').show();
      $('.btn-success').css("margin-right",420);
      
      var w = $(window).width()*0.31;
      $('.annotator-widget').width(w);
      
    /*}
    else {
      $('#splitter').jqxSplitter({
        width: 1270,
        height: '100%',
        panels: [{size: '100%', min: 100}, {size: '0%', min: 0}]
      });
      $('.btn-success').val("hide");
    }*/

  }