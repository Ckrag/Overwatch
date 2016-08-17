
$(document).ready(function() {
    setup();
});

function setup(){
    var moduleElements = document.getElementsByClassName("module_frame");
    var module_height = $(window).height()

    $(".module_frame").css("height", ($(window).height() / moduleElements.length) + "px")
}