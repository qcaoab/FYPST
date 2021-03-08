

//select file to be uploaded
function readURL(input) {
    if (input.files && input.files[0]) {
        var reader = new FileReader();
    
        reader.onload = function (e) {
            $('filename')
                .attr('src', e.target.result)
                .width(150)
                .height(200);
        };
    
        reader.readAsDataURL(input.files[0]);
    }

}
var filename;
function stopImageUpload(success){

    function handleFileSelect(evt) {
    var files = evt.target.files;
    filename = files[0].name; //save the name for future use
}

$('.fileImage').bind('change', handleFileSelect, false);


        var result = '';
        if (success == 1){
    result = '<span class="msg">The file ('+filename+') was uploaded successfully!</span><br/><br/>';
    fileName = ""; //remove the temporary variable

        }
        else {
            result = '<span class="emsg">There was an error during file upload!</span><br/><br/>';
        }

        return true;   
}


function preview() {
    imgInp.src=URL.createObjectURL(event.target.files[0]);
}

var test = document.getElementById("dropdown_selection");
var testValue = test.options[test.selectedIndex].value;
document.getElementById('message').innerHTML=testValue;

