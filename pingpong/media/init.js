// INIT LOADER /////////////////////////////
// Pre-loads all JS and popups for the entire app
/***************************/
//@Author: Adrian "yEnS" Mato Gondelle & Ivan Guardado Castro
//@website: www.yensdesign.com
//@email: yensamg@gmail.com
//@license: Feel free to use it, but keep this credits please!					
/***************************/
var LoadBar = function(){
	this.value = 0;
	this.sources = Array();
	this.sourcesDB = Array();
	this.totalFiles = 0;
	this.loadedFiles = 0;
};
//Show the loading bar interface
LoadBar.prototype.show = function() {
	document.getElementById("loading").style.display = "block";
};
//Hide the loading bar interface
LoadBar.prototype.hide = function() {
	document.getElementById("loading").style.display = "none";
};
//Add all scripts to the DOM
LoadBar.prototype.run = function(){
	this.show();
	var i;
	for (i=0; i<this.sourcesDB.length; i++){
		var source = this.sourcesDB[i];
		var head = document.getElementsByTagName("head")[0];
		var script = document.createElement("script");
		script.type = "text/javascript";
		script.src = source;
		head.appendChild(script);
	}	
};
//Set the value position of the bar (Only 0-100 values are allowed)
LoadBar.prototype.setValue = function(value){
	if(value >= 0 && value <= 100){
		document.getElementById("progressBar").style.width = value + "%";
	}
};
//Add the specified script to the list
LoadBar.prototype.addScript = function(source){
	this.totalFiles++;
	this.sources[source] = source;
	this.sourcesDB.push(source);
};
//Called when a script is loaded. Increment the progress value and check if all files are loaded
LoadBar.prototype.loaded = function(file) {
	this.loadedFiles++;
	delete this.sources[file];
	var pc = (this.loadedFiles * 100) / this.totalFiles;
	this.setValue(pc);
	//Are all files loaded?
	if(this.loadedFiles == this.totalFiles){
		setTimeout("myBar.hide()",300);
		//load the reset button to try one more time!
		document.getElementById("app").style.display = "block";
	}
};
//Global var to reference from other scripts
var myBar = new LoadBar();
//Checking resize window to recenter :)
window.onresize = function(){
	myBar.locate();
};
//Called on body load
start = function(){
	myBar.addScript("core.js");
	myBar.run();
};