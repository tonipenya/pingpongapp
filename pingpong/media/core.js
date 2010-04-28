// #############################
// 1) ONLOAD
// #############################
// Set init arrays
teamone = new Array();
teamtwo = new Array();
// Set events
$(document).ready(function () {
	determineLayout();
});
$(window).resize(function () {
	determineLayout();
});
$('.nav_singles').live('click', function() {
	$(".nav_singles").removeClass("nav_up").addClass("nav_down");
	$(".nav_doubles").removeClass("nav_down").addClass("nav_up");
	$("#doubles").hide();
	$("#singles").fadeIn("slow");
	return false;
});
$('.nav_doubles').live('click', function() {
	$(".nav_doubles").removeClass("nav_up").addClass("nav_down");
	$(".nav_singles").removeClass("nav_down").addClass("nav_up");
	$("#singles").hide();
	$("#doubles").fadeIn("slow");
	return false;
});
$('#players').live('click', function() {
	signupHideExample();						 
});
$('#players').live('focus', function() {
	signupHideExample();						 
});
$('#signup_players_example').live('click', function() {
	signupHideExample();						 
});	
// #############################
// 2) CORE
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
// 3) SECTIONS
// #############################
// ADD SCORES ///////////////////////////
$('div.add_player').live('click', function() {
  var playerID = $(this).attr("id");
	var player = $(this).attr("name");
	var team = $(this).attr("team");
	// If it's already selected unselect it
	if ($(this).hasClass("selected")) {
		$(this).removeClass("selected");
		playersRemove(team, playerID);
	} else {
		// Max of 2 players per team
		if (playersCheckMax(team)) {
			// Check that players not already selected on other team
			checkOtherTeam = playersCheckOtherTeam(team, playerID);
			if (checkOtherTeam === -1) {
				$(this).addClass("selected");
				playersAdd(team, playerID);
			} else {
				var otherTeam = (team === "one") ? "two" : "one";
				alert(player +" has already been selected as a player on team "+ otherTeam);
			}
		} else {
			alert("Oops, you can only select two players per team");
		}
	}
	return false;
});
function playersAdd (team, playerID) {
	if (team === "one") {
		teamone.push(playerID);
	} else {
		teamtwo.push(playerID);
	}
}
function playersCheckMax (team) {
	if (team === "one") {
		var lVal = teamone.length
	} else {
		var lVal = teamtwo.length;
	}
	if (lVal >= 2) {
		return false;
	} else {
		return true
	}
}
function playersCheckOtherTeam (team, playerID) {
	var teamArray = (team === "one") ? teamtwo : teamone;
	return teamArray.indexOf(playerID);
}
function playersRemove (team, playerID) {
	if (team === "one") {
		playersRemoval(teamone, playerID);
	} else {
		playersRemoval(teamtwo, playerID);
	}
}
function playersRemoval (arr, value) {
	arr.splice($.inArray(value, arr), 1);
}
function serializeScores (one, two) {
	return "t1p1="+one[0]+"&t1p2="+one[1]+"&t2p1="+two[0]+"&t2p2="+two[1];
}
function submitScores () {
	// Grab values
	var teamOneScore = $("#teamOneScore").text();
	var teamTwoScore = $("#teamTwoScore").text();
	// piece together serialized string
	var str = serializeScores(teamone, teamtwo)+"&t1s="+teamOneScore+"&t2s="+teamTwoScore;
	$.ajax({
		url: "/score/add/",
		type: "POST",
		data: str,
		success : function (data) {
			var submitStatus = data.status; // true if success, otherwise false
			if (submitStatus) {
				// Reset add form
				$(".selected").removeClass("selected");
				$("#teamOneScore").text("0");
				$("#teamTwoScore").text("0");
				$("#teamOneSlider").slider( "option", "value", 0 );
				$("#teamTwoSlider").slider( "option", "value", 0 );
				showMessage(data.message);
				setTimeout("redirectAfterAddScore();", 1500);
			} else {
				// show error provided in JSON response something like "Only two players can be selected per team."
				showMessage(data.message);
			}
		}
	});
}
function redirectAfterAddScore() { window.location.replace("/"); }
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
	hideMessage();
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
		window.scrollTo(0,0);
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
				window.scrollTo(0,0);
			}
		});
	}
}
// SETTTINGS /////////////////////////////
function settingsAdd () {
	$("#settings_add").show();
}
function settingsDelete (user, userid) {
	if (confirm("Are you sure you want to delete "+user+"? All of their scores will be lost.")) {
		ajax ("PATHTOUSERDELETE", "GET", "", "settingsDeleteMethod", "", "");
  	}
}
function settingsDeleteMethod (data) {
	$("#popup_settings").remove();
	$("#popup_container").prepend(data);
	var tWidth = $(window).width();
	var tPopup = $("#popup_settings").width();
	$("#popup_settings").css("left", [tWidth-tPopup]/2+"px");
}
function settingsEdit(userid) {
	if ($('#'+userid+"_input").is(':visible')) {
		$('#'+userid+"_name").show();
		$('#'+userid+"_input").hide();
		$('#'+userid+"_edit").text("edit");
	} else {
		$('#'+userid+"_name").hide();
		$('#'+userid+"_input").show();
		$('#'+userid+"_input input").select();
		$('#'+userid+"_edit").text("cancel");
	}
}
// SIGNUP /////////////////////////////
function signupCheckUsername (username) // Checks if username is available
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
function signupCheckUsernameMethod (data)
{
	$("#core_uname_confirm").html(data);
}
function signupForm ()
{
	ajax(baseUrl+"auth/signup", "POST", "", "signupFormMethod", "signups", "");
}
function signupFormMethod (data) {
	$("#popup_freetrial").remove();
	$("#popup_container").prepend(data);
	var tWidth = $(window).width();
	var tPopup = $("#popup_freetrial").width();
	$("#popup_freetrial").css("left", [tWidth-tPopup]/2+"px");
}
function signupHideExample () {
	$('#signup_players_example').hide();
	$('#players').select();
}