var brightnessInPercentage = 100;
var contrastInPercentage = 100;
var rotationInDegree = 0;
var moveOnX = 0;
var moveOnY = 0;
var num = 0;
var pathToImage = "crop_image/?photo={{photourl}}&id={{photoid}}";


function setTextVisibility() {

  document.getElementById("textOnImage").textContent = document.getElementById("textOnImageValue").value;
  //document.getElementById("textOnImage").textContent = "HI";
  document.getElementById("textOnImage").style = "position: absolute; visibility: visible; z-index: 1;";

};

function removeText() {
  document.getElementById("textOnImageValue").value = "";
  //document.getElementById("textOnImage").textContent = "HI";
  document.getElementById("textOnImage").style = "position: absolute; visibility: hidden; z-index: 1;";
}

function moveText() {
  moveOnX = document.getElementById("textMoveOnX").value;
  moveOnY = document.getElementById("textMoveOnY").value;

  document.getElementById("spanMoveXValue").textContent = moveOnX+"%";
  document.getElementById("spanMoveYValue").textContent = moveOnY+"%";

  document.getElementById("textOnImage").style = "z-index: 1;position: absolute; visibility: visible; margin-top: "+moveOnY+"%; margin-left: "+moveOnX+"%;";

}


function setHrefToCropButton() {

  document.getElementById("goToCrop").setAttribute("href", "crop_image/?photo="+pathToImage+"&id={{photoid}}");
  alert(pathToImage);

};

function cropImage() {
  
  //alert(document.getElementById("dataX").value);
  $.ajax({
    url : "save_cropped_image/", // the endpoint
    type : "GET", // http method
    data : {x: document.getElementById("dataX").value, 
            y: document.getElementById("dataY").value,
            height: document.getElementById("dataHeight").value,
            id: document.getElementById("aPhotoId").textContent,
            width: document.getElementById("dataWidth").value }, // data sent with the get request

    // handle a successful response
    success : function(json) {
        console.log("success, cropped"); // another sanity check
        
    },

    // handle a non-successful response
    error : function(xhr,errmsg,err) {
        console.log(xhr.status + ": " + xhr.responseText); // provide a bit more info about the error to the console
    }
  });

};

function saveImage() {
  
  $.ajax({
    url : "save_image/", // the endpoint
    type : "GET", // http method
    data : {brightness : brightnessInPercentage, 
            contrast : contrastInPercentage,
            rotation: rotationInDegree,
            textX: moveOnX,
            textY: moveOnY,
            textValue: document.getElementById("textOnImageValue").value,
            id: document.getElementById("aPhotoId").textContent,
            photo: document.getElementById("imageforchanging").src }, // data sent with the get request

    // handle a successful response
    success : function(json) {
        console.log("success"); // another sanity check
        // alert(json.filepath)
        pathToImage = json.filepath;
        setHrefToCropButton();
    },

    // handle a non-successful response
    error : function(xhr,errmsg,err) {
        console.log(xhr.status + ": " + xhr.responseText); // provide a bit more info about the error to the console
    }
  });
};

function changeBrightness(bValue) {
    brightnessInPercentage = bValue;
    document.getElementById("spanBrightnessValue").textContent=bValue+"%";
    setStyleToImage();
};

function changeContrast(cValue) {
    contrastInPercentage = cValue;
    document.getElementById("spanContrastValue").textContent=cValue+"%";
    setStyleToImage();
};

function changeRotation(rValue) {
    rotationInDegree = rValue;
    document.getElementById("spanRotationValue").textContent=rValue+"°";
    setStyleToImage();
};

function setStyleToImage() {

    centered = "display: block; margin:auto;";
    rotation = "transform: rotate("+rotationInDegree+"deg);"
    contrast = "contrast("+contrastInPercentage+"%) ";
    brightness = "brightness("+brightnessInPercentage+"%)";
    filters = "filter: "+contrast+brightness;

    document.getElementById("imageforchanging").style = centered+rotation+filters;

    


};

