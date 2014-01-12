/**
 * Created by Alex on 27.10.13.
 */
jQuery(document).ready(function ($) {
    $(".clickableRow").click(function () {
        window.document.location = $(this).attr("href");
    });
});
$(document).ready(function () {
    $('.submit').keydown(function (event) {
        if (event.keyCode == 13) {
            this.form.submit();
            return false;
        }
    });
});