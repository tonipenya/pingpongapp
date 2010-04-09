// #############################
// 1) CORE
// #############################
// AJAX LOADER /////////////////////////
function ajax (url, type, id, method, formid, message) {
	if (formid) { var str = $("#"+formid).serialize(); } else { var str = ""; } // Serialize form contents
	$.ajax({
		url: url, // URL of request
		type: type, // GET or POST
		data: str,
		beforeSend: function(){
			if (message)
			{
				showMessage(message);
			}
		},
		success : function (data) {
			if (id) { $("#"+id).html(data); } // ID to populate on success
			if (method) { window[method](data); } // Call this method on success
		},
		complete: function(){
			hideMessage();
		}
	});
	/*error:function (xhr, ajaxOptions, thrownError){
		alert(xhr.status);
		alert(thrownError);
	}*/   
}
function determineLayout () {
	windowWidth = $(window).width();
	mainDivWidth = windowWidth-35;
	if (windowWidth <= 786) {
		totalCols = 1;
		resizeCols();
	} else if (windowWidth > 786 && windowWidth < 1252) {
		totalCols = 2;
		resizeCols();
	} else {
		totalCols = 3;
		resizeCols();
	}
}
function resizeCols () {
	var colWidth = (mainDivWidth/totalCols)-68;
	// Set col width
	$(".core_the_rest").css("width", colWidth+"px");
}
// #############################
// 2) SECTIONS
// #############################
// FEEDBACK ///////////////////////////
function getFeedback ()
{
	feedback_widget.show();
}
// MESSAGES /////////////////////////////
function hideMessage ()
{
	$("#message").fadeOut("slow");
}
function showMessage (message)
{
	$("#message").html(message);
	totalWidth = $(window).width();
	messageWidth = $("#message").width();
	$("#message").css("left", [totalWidth-messageWidth]/2+"px")
	$("#message").show();
}
// LOGIN /////////////////////////////
function loginCheckUsername (username) // Checks if username is available
{
	$("#uname_error").hide();
	var ulength = username.length
	if (ulength > 3)
	{
		ajax(baseUrl+'auth/check/'+username, "GET", "", "loginCheckUsernameMethod", "", "");
	}
	else
	{
		$("#core_uname_confirm").html('<span class="core_error">Shop names must be at least 4 characters long</span>');
	}
}
function loginCheckUsernameMethod (data)
{
	$("#core_uname_confirm").html(data);
}
function doLogin() {
	$("#popup_login").hide();
	showMessage('Logging in...');
	ajax("/login/ajax", "POST", "", "loginCallback", "loginForm", "");
}
function loginCallback(data) {
	if (data === "false") {
		hideMessage();
		$("#login_error").val("Your username or password is invalid");
		$("#login_error").show();
		var tWidth = $(window).width();
		var tPopup = $("#popup_login").width();
		$("#popup_login").css("left", [tWidth-tPopup]/2+"px");
	} else {
		window.location = data;
	}
}
function loginClear (which) {
	if (which === "username") {
		var loginUsername = $("#loginUsername").val();
		if (loginUsername === "Username") {
			$("#loginUsername").val("");
		}
	} else {
		var loginPassword = $("#loginPassword").val();
		if (loginPassword === "Password") {
			$("#loginPassword").val("");
		}
	}
}
function loginFormValue () {
	var loginUsername = $("#loginUsername").val();
	var loginPassword = $("#loginPassword").val();
	if (loginUsername === "" || loginUsername === "Username") {
		$("#loginUsername").val("Username");
		$("#loginUsername").css("color", "#999");
	} else {
		$("#loginUsername").css("color", "#333");
	}
	if (loginPassword === "" || loginPassword === "Password") {
		$("#loginPassword").val("Password");
		$("#loginPassword").css("color", "#999");
	} else {
		$("#loginPassword").css("color", "#333");
	}
}
// LOADING /////////////////////////////
function coreLoading (message)
{
	$("#core_loading").html(message);
	$("#core_loading").fadeIn();
}
// POPUPS /////////////////////////////
function hideShade () // Hides all popups and shade
{
	$("#core_shade").hide();
	$(".popup").hide();
}
function preloadPopup (popup, url)
{
	if ( $("#popup_"+popup).length == 0 ) {
		var tWidth = $(window).width();
		$.ajax({
			url: baseUrl+url,
			type: "GET",
			success : function (data) {
				$("#popup_container").prepend(data);
				var tPopup = $("#popup_"+popup).width();
				$("#popup_"+popup).css("left", [tWidth-tPopup]/2+"px");
			}
		});
	}
}
function showPopup (popup, url, focus) // Show or load popup
{
	var docHeight = $(document).height();
	// Clear current popup
	$(".popup").hide();
	// Show shade
	$("#core_shade").css("height", docHeight+300);
	$("#core_shade").show();
	// If div exists, show it, else load it
	if ( $("#popup_"+popup).length > 0 ) {
		$("#popup_"+popup).show();
		if (focus) { $("#"+focus).focus(); }
	} else {
		showMessage('Loading...');
		var tWidth = $(window).width();
		$.ajax({
			url: baseUrl+url,
			type: "GET",
			success : function (data) {
				$("#popup_container").prepend(data);
				var tPopup = $("#popup_"+popup).width();
				$("#popup_"+popup).css("left", [tWidth-tPopup]/2+"px");
				if (focus) { $("#"+focus).focus(); }
				hideMessage();
				$("#popup_"+popup).show();
			}
		});
	}
}
// SIGNUP /////////////////////////////
function signupForm ()
{
	ajax(baseUrl+"auth/signup", "POST", "", "signupFormMethod", "signupForm", "");
}
function signupFormMethod (data) {
	$("#popup_signup").remove();
	$("#popup_container").prepend(data);
	var tWidth = $(window).width();
	var tPopup = $("#popup_signup").width();
	$("#popup_signup").css("left", [tWidth-tPopup]/2+"px");
}
// #############################
// 3) PLUGINS
// #############################