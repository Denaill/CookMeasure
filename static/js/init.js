(function($) {
    $(function() {

        $('.sidenav').sidenav();
        $('.carousel').carousel({ dist: -40, indicator: true });
        $('.tabs').tabs();
        $('.tooltipped').tooltip();
        $('.materialboxed').materialbox();
        $('.modal').modal();
    }); // end of document ready
})(jQuery); // end of jQuery name space

$('.chips').chips();
  $('.chips-initial').chips({
    data: [{
      tag: 'Carne',
    }, {
      tag: 'Cerdo',
    }, {
      tag: 'Pollo',
    }],
  });
  $('.chips-placeholder').chips({
    placeholder: 'Añadir ingredientes',
    secondaryPlaceholder: '+ Ingredientes',
  });
$('.dropdown-trigger').dropdown();
$('#preparacion').val('Porfavor especifica la preparación de la receta');
M.textareaAutoResize($('#preparacion'));