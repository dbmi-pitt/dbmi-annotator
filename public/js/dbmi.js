$(document).ready(function () {
    $('#splitter').jqxSplitter({ width: '100%', height: '100%',  panels: [{ size: '100%', min: 100 }, { size: '0%', min: 0}] });
  });

//show right splitter by button "btn-success"
  function showrightbyvalue(){
    
    if($('.btn-success').val()=="hide") {
      
      $('#splitter').jqxSplitter({
        width: '100%',
        height: '100%',
        panels: [{size: '67%', min: 850}, {size: '33%', min: 410}]
      });
      $('.btn-success').val("show");
      $('.annotator-editor').show();
      $('.btn-success').css("margin-right",430);
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

  }

//show right splitter directly
  function showright(){
    
      $('#splitter').jqxSplitter({
        width: '100%',
        height: '100%',
        panels: [{size: '67%', min: 850}, {size: '33%', min: 410}]
      });
      $('.btn-success').val("show");
      $('.annotator-editor').show();
      $('.btn-success').css("margin-right",420);
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