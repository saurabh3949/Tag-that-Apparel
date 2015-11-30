var getResults = function() {
    $("#submit_button").button("loading");
    $.post("/geturl", {
            url: $("#url").val()
        },
        function(data, status) {
            // alert(data);
            var imageURL = $("#url").val();
            var object = jQuery.parseJSON(data);
            var cloth = object[0];
            var color = object[1];
            var i = 1;
            $.each(cloth, function(key, value) {
                var newValue = (parseFloat(value) * 100).toString();

                $("#cloth" + i.toString() + "_text").text(key);
                $("#cloth" + i.toString()).attr("style", "width:" + newValue + "%");
                i = i + 1;
            });
            var i = 1;
            $.each(color, function(key, value) {
                var newValue = (parseFloat(value) * 100).toString();

                $("#color" + i.toString() + "_text").text(key);
                $("#color" + i.toString()).attr("style", "width:" + newValue + "%");
                i = i + 1;
            });
            $("#submit_button").button('reset');
            $("#results-row").removeClass("hidden");
            $("#image-placeholder").attr("src", imageURL);

            // alert("Data: " + data + "\nStatus: " + status);
        }).error(function() {
        $("#results-row").addClass("hidden")
        $("#error").append('<div class="alert alert-info" id="error">Ooops! There was some problem in downloading that image. Please try using a different one! <a href="#" class="close" data-dismiss="alert" aria-label="close">&times;</a></div>');
        $("#submit_button").button('reset');

    });
};

$(document).ready(function() {


    $("#url").keypress(function(e) {
        if (e.which == 13) {
            getResults();
        }
    });



    $("#submit_button").click(getResults);


});
