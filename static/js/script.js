$(function() {
	function resetTabs(){
		$("#content div").hide();
		$("#tabs a").attr("id",""); 
	}

	var myUrl = window.location.href;
	var myUrlTab = myUrl.substring(myUrl.indexOf("#"));
	var myUrlTabName = myUrlTab.substring(0,3);

	(function(){
		$("#content div").hide();
		$("#tabs li:first a").attr("id","current");
		$("#content div:first").fadeIn();

		$("#tabs a").on("click",function(e) {
			e.preventDefault();
			if ($(this).attr("id") == "current"){
				return
			}
			else{
				resetTabs();
				$(this).attr("id","current");
				$($(this).attr('name')).fadeIn();
			}
		});
		for (i = 1; i <= $("#tabs li").length; i++) {
			if (myUrlTab == myUrlTabName + i) {
				resetTabs();
				$("a[name='"+myUrlTab+"']").attr("id","current");
				$(myUrlTab).fadeIn();
			}
		}
	})()
});