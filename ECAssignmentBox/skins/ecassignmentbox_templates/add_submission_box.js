var createdFiles;

$(document).ready(function() {
	
	createdFiles = 0;	
	//hide add and remove button if necessary
	if (maxFiles == 0) {
		$("#addSubmissionButton").hide();
	}
	$("#removeSubmissionButton").hide();
});

function addSubmissionBox() {
	$(document).ready(function(){
	
		//get submissionBox
		var subBox = $("#submissionBox").clone();
		//delete reference to answer template
		$(subBox).find("textarea").val("");
		//delete content of upload field
		$(subBox).find("input").val("");
		//append box to ecab_view
		subBox.appendTo("#submissionTemplate");
		//check createdFiles and hide add button, if enough boxes are provided
		createdFiles++;
		if (createdFiles >= maxFiles) {
			$("#addSubmissionButton").hide();
		}	
		//show remove button
		$("#removeSubmissionButton").show();
	});
}

function removeSubmissionBox() {
	$(document).ready(function(){
		//check if a submission box can be removed removed
		if (createdFiles > 0) {
			//remove last submission box
			$("#submissionBox:last-child").remove();
			//decrement createdFiles
			createdFiles--;			
		}		
		//hide remove button, if only one submission box left
		if (createdFiles == 0) {
			$("#removeSubmissionButton").hide();
		}		
		//show add button
		$("#addSubmissionButton").show();		
	});
}
		