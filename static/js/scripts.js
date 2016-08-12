//
//var xhr = new XMLHttpRequest();
//xhr.onreadystatechange = function () {
//  if(xhr.readyState === 4 && xhr.status === 200) {
//    var types = JSON.parse(xhr.responseText);
//    var statusHTML = "";
//    for (var i=0; i<types.length; i += 1) {
//        statusHTML += '<option value="';
//        statusHTML += types[i].item_id;
//        statusHTML += '">';
//        statusHTML += types[i].item_type;
//        statusHTML += '</option>';
//    }
//    document.getElementById('first').innerHTML = statusHTML;
//
//
//  }
//};
//xhr.open('GET', '.../item_types.json');
//xhr.send();

var $item_select = $('#item_type');
var $model_select = $('#item_model');

var url = "static/data/item_types.json";
$.getJSON(url, function (response) {
    var statusHTML = '<option value="0">Select a type</option>';
    $.each(response, function(index, item_type) {
        statusHTML += '<option value="';
        statusHTML += item_type.item_id;
        statusHTML += '">' + item_type.item_type;
        statusHTML += '</option>'
    });
    $item_select.html(statusHTML);
}); // end getJSON

//var url = "static/data/models.json";
//$.getJSON(url, function (response) {
//    var statusHTML = '';
//    $.each(response, function(index, item_type) {
//        statusHTML += '<option value="';
//        statusHTML += item_type.item_id;
//        statusHTML += '>' + item_type.item_type;
//        statusHTML += '</option>'
//    });
//    $('#second').html(statusHTML);
//}); // end getJSON

// First attempt at dependent select box
$item_select.change(function() {

    if ($item_select.val() === "0") {
        $model_select.html('<option value="0">Select a type first</option>');
    } else {
        $.getJSON('static/data/models.json', function(response) {
            var model_options_HTML = '';
            $.each(response, function(index, model) {
                if($item_select.val().toString() === model.of_type.toString()) {
                    model_options_HTML += '<option value="' + model.model_id;
                    model_options_HTML += '">' + model.name;
                    model_options_HTML += '</option>';
                    alert(model_options_HTML);
                }
                $model_select.html(model_options_HTML);
            });
        });
    }
});