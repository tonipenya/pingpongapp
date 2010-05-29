// #############################
// 1) ONLOAD
// #############################
// Set init arrays
var teamone = new Array();
var teamtwo = new Array();
var preventDoubleSubmission = true;
// Set events
$(document).ready(function () {
	determineLayout();
	var price = $("#price").text() || "$8.95";
});
$(window).resize(function () {
	determineLayout();
});
$('.nav_singles').live('click', function() {
  showSingles();
	return false;
});
$('.nav_doubles').live('click', function() {
  showDoubles();
	return false;
});
var currentMode = 'singles';
function showSingles() {
	$(".nav_singles").removeClass("nav_up").addClass("nav_down");
	$(".nav_doubles").removeClass("nav_down").addClass("nav_up");
	$("#doubles").hide();
	$("#singles").fadeIn("slow");
	currentMode = 'singles';
}
function showDoubles() {
	$(".nav_doubles").removeClass("nav_up").addClass("nav_down");
	$(".nav_singles").removeClass("nav_down").addClass("nav_up");
	$("#singles").hide();
	$("#doubles").fadeIn("slow");
	currentMode = 'doubles';
}
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
// Used to retrieve query string param values by name
function getParameterByName(name) {
  name = name.replace(/[\[]/,"\\\[").replace(/[\]]/,"\\\]");
  var regexS = "[\\?&]"+name+"=([^&#]*)";
  var regex = new RegExp( regexS );
  var results = regex.exec( window.location.href );
  if (results == null)
    return "";
  else
    return results[1];
}
function htmlEncode(value) {
  return $('<div/>').text(value).html(); 
} 
function htmlDecode(value) {
  return $('<div/>').html(value).text(); 
}
// AJAX LOADER /////////////////////////
function ajax (url, type, id, method, formid, message, str) {
	if (formid) { // Serialize form contents
		var str = $("#"+formid).serialize();
	} else {
		if (!str) {
			var str = "";
		}
	} 
	if (preventDoubleSubmission) {
		$.ajax({
			url: url, // URL of request
			type: type, // GET or POST
			data: str,
			beforeSend: function(){
				preventDoubleSubmission = false;
				if (message)
				{
					showMessage(message);
				}
			},
			success : function (data) {
				if (id) { $("#"+id).html(data); } // ID to populate on success
				if (method) { method(data); } // Call this method on success
			},
			complete: function(){
				hideMessage();
				if (formid) { $("#"+formid).resetFormSubmissions(); }
				preventDoubleSubmission = true;
			},
			error:function (xhr, ajaxOptions, thrownError){
				if (formid) { $("#"+formid).resetFormSubmissions(); }
				preventDoubleSubmission = true;
			}
		});
	}
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
	if (windowWidth <= 755) {
		$('body').addClass("mobile");
	} else {
		$('body').removeClass("mobile");
	}
}
function resizeCols () {
	if (totalCols > 1) {
		var colWidth = (mainDivWidth/totalCols)-59;
		// Set col width
		$(".core_the_rest").css("width", colWidth+"px");
	} else {
		$(".core_the_rest").removeAttr("style");
	}
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
				showMessage(player +" has already been selected as a player on team "+ otherTeam);
				setTimeout("hideMessage();", 2000);
			}
		} else {
			showMessage("Oops, you can only select two players per team");
			setTimeout("hideMessage();", 2000);
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
	// Ensure that there are scores and that they aren't equal
	if (teamOneScore && teamTwoScore && teamOneScore !== teamTwoScore) {
		// Ensure that players are selected on both teams
		if (teamone.length > 0 && teamone.length < 3 && teamtwo.length > 0 && teamtwo.length < 3) {
			// Ensure same number of players on both sides
			if (teamone.length === teamtwo.length) {
				// piece together serialized string
				var str = serializeScores(teamone, teamtwo)+"&t1s="+teamOneScore+"&t2s="+teamTwoScore;
				// Make POST
				ajax ("/score/add/", "POST", "", submitScoresMethod, "", "Calculating new rankings...", str);
				// Prevent double submissions
			} else {
				showMessage("Oops, you've got to have the same number of players on both teams.");
				setTimeout("hideMessage();", 2500);
			}
		} else {
			showMessage("Don't forget to add players to both sides");
			setTimeout("hideMessage();", 2000);
		}
	} else {
		showMessage("Don't forget to add scores, and they can't be equal.");
		setTimeout("hideMessage();", 2000);
	}
}
function submitScoresMethod (data) {
	var submitStatus = data.status; // true if success, otherwise false
	if (submitStatus) {
		// Reset add form
		$(".selected").removeClass("selected");
		$("#teamOneScore").text("0");
		$("#teamTwoScore").text("0");
		$("#teamOneSlider").slider( "option", "value", 0 );
		$("#teamTwoSlider").slider( "option", "value", 0 );
		setTimeout(function(){redirectAfterAddScore(data.mode)}, 1000);
		$(".popup").hide();
	} else {
		// show error provided in JSON response something like "Only two players can be selected per team."
		showMessage(data.message);
	}
}
function redirectAfterAddScore(mode) {
  window.location.replace("/?m=" + mode);
}
function presetScore (points, team) {
	$("#team"+team+"Slider .ui-slider-handle").css("left", points*3.33333+"%");
	$("#team"+team+"Score").html(points);
}
// ANALYTICS //////////////////////////
function fakePageview (pageName) {
	pageTracker._trackPageview(pageName);
}
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
	ajax("/login/ajax", "POST", "", loginCallback, "loginForm", "", "");
	$("#"+loginForm).blockDoubleSubmissions();
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
function logOut (url) {
	fakePageview(url); // track in GA
	window.location = url;
}
// LOADING /////////////////////////////
function coreLoading (message)
{
	$("#core_loading").html(message);
	$("#core_loading").fadeIn();
}
// POPUPS /////////////////////////////
function fullPageLoading (message)
{
	$("#core_loading").html(message);
	$("#core_loading").fadeIn();
}
function hideShade () // Hides all popups and shade
{
	$("#core_shade").hide();
	$(".popup").hide();
	hideMessage();
	$(".formError").hide();
}
function preloadPopup (popup, url)
{
	if ( $("#popup_"+popup).length == 0 ) {
		ajax (url, "GET", "", preloadPopupMethod, "", "", "");
	}
}
function preloadPopupMethod (data) {
	var tWidth = $(window).width();
	$("#popup_container").prepend(data);
	var tPopup = $("#popup_"+popup).width();
	$("#popup_"+popup).css("left", [tWidth-tPopup]/2+"px");
}
function showPopup (popup, url, focus) // Show or load popup
{
	// Set popup name for method
	popupName = popup;
	// Add fake pageview to Google Analytics
	fakePageview(url);
	// Grab doc height
	var docHeight = $(document).height();
	// Clear current popup
	$(".popup").hide();
	// Show shade
	$("#core_shade").css("height", docHeight+300);
	$("#core_shade").show();
	// Fix 2 col bug
	determineLayout();
	// If div exists, show it, else load it
	if ( $("#popup_"+popup).length > 0 ) {
		$("#popup_"+popup).show();
		if (focus) { $("#"+focus).focus(); }
		window.scrollTo(0,0);
	} else {
		ajax (url, "GET", "", showPopupMethod, "", "Loading...", "");
	}
}
function showPopupMethod (data) {
	var tWidth = $(window).width();
	$("#popup_container").prepend(data);
	var tPopup = $("#popup_"+popupName).width();
	$("#popup_"+popupName).css("left", [tWidth-tPopup]/2+"px");
	if (focus) { $("#"+focus).focus(); }
	hideMessage();
	$("#popup_"+popupName).show();
	window.scrollTo(0,0);
}
// SETTTINGS /////////////////////////////
function settingsAdd() {
  if ($("#settings_add").is(':visible')) {
    $("#players").val('');
    $('#signup_players_example').show();
    $("#settings_add").hide();
    $("a#add_new_players").text('Add new players');
  } else {
    $("#settings_add").show();
    $("a#add_new_players").text('cancel');
  }
}
function deletePlayer(player, playerKey) {
	if (confirm("Are you sure you want to delete " + player + "?")) {
		ajax ("/player/delete/" + playerKey, "POST", "", deletePlayerMethod, "", "Calculating new rankings...", "");
	}
}
function deletePlayerMethod (data) {
	if (data.status) { // true if success, otherwise false
		showMessage(data.message);
		setTimeout(function(){redirectAfterDeletePlayer()}, 1000);
		$(".popup").hide();
	} else {
		showMessage(data.message);
	}
}
function redirectAfterDeletePlayer() {
  modeStr = currentMode === 'doubles' ? '?m=doubles' : '';
  window.location.replace("/" + modeStr);
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
function serializeSettings() {
  result = '';
  // Add email address
  result+= 'email=' + encodeURIComponent($("#email").val()) + '&';
  // Add any new player data
  result += 'newplayers=' + encodeURIComponent($("textarea#players").val()) + '&';
  // Find players whose names have changed and serialise
  $("div[id$='_input']:visible input").each(function() {
    result += $(this).attr('id') + '_player=' + encodeURIComponent($(this).attr('value')) + '&';
  });
  return result.substr(0, result.length - 1);
}
function submitSettings() {
	if ($("#settings").valid()) {
		var str = serializeSettings();
		ajax ("/settings/", "POST", "", submitSettingsMethod, "", "Saving settings...", str);
	}
}
function submitSettingsMethod (data) {
	var submitStatus = data.status; // true if success, otherwise false
	if (submitStatus) {
		showMessage(data.message);
		setTimeout(function(){redirectAfterSubmitSettings()}, 1000);
		$(".popup").hide();
	} else {
	  showSettingsErrors(data.errors);
		showMessage(data.message);
	}
}
function clearSettingsErrors() {
  $(".error").each( function() {
    $(this).text('');
  });
}
function showSettingsErrors(errors) {
  clearSettingsErrors();
  $.each(errors, function(id, error) {
    if ($("#" + id + "_error")) {
		$("#" + id + "_error").text(error);
	} else {
		$("#" + id).after('<label id="'+id+'_error" for="'+id + "_error"+'" generated="true" class="error">'+error+'</label>');
	}
  });
}
function redirectAfterSubmitSettings() {
  modeStr = currentMode === 'doubles' ? '?m=doubles' : '';
  window.location.replace("/" + modeStr);
}
// SIGNUP /////////////////////////////
function signupCheckUsername (username) // Checks if username is available
{
	$("#uname_error").hide();
	var ulength = username.length
	if (ulength > 3)
	{
		ajax('auth/check/'+username, "GET", "", signupCheckUsernameMethod, "", "", "");
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
	if ($("#signup").valid()) {
		ajax("auth/signup", "POST", "", signupFormMethod, "signups", "", "");
	}
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
// UPGRADE /////////////////////////////
function upgrade (plan)
{
	fullPageLoading("One moment...");
	window.location.replace("/paypal/");
}