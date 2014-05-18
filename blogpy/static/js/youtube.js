var width = 584
var height = 329

String.prototype.format = function() {
	var formatted = this;
	for (var i = 0; i < arguments.length; i++) {
		var regexp = new RegExp('\\{'+i+'\\}', 'gi');
		formatted = formatted.replace(regexp, arguments[i]);
	}
	return formatted;
};

$(function() {
	$(".youtube-preview").on("click", function(e) {
		var iframe = '<iframe class="youtube-player" type="text/html" ' +
					 'width="{0}" height="{1}" ' +
					 'src="http://www.youtube.com/embed/{2}?autoplay=1" ' +
					 'frameborder="0"></iframe>';
		$(this).replaceWith(iframe.format(width, height, $(this).attr("id")));
	});
});