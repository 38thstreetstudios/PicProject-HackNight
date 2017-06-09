$(document).ready(function() {

	$(".topic-button").click(function() {
        var title = $(this).parent().siblings('.topic-title').text();
		window.location.href = "/" + $(this).attr('id') + "/" + title;
    });
});