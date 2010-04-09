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