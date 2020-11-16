

setTimeout(setRotate, 3000);


var newImageZIndex = 1;         // To make sure newly-loaded images land on top of images on the table
var loaded = false;             // Used to prevent initPhotos() running twice
var imageBeingRotated = false;  // The DOM image currently being rotated (if any)
var mouseStartAngle = false;    // The angle of the mouse relative to the image centre at the start of the rotation
var imageStartAngle = false;

function setRotate() {
    //alert("ok");



    // The table image has loaded, so bring in the table
    //$('.rotated').fadeIn('fast');

    // Add an event handler to stop the rotation when the mouse button is released
    $(document).mouseup(stopRotate);

    // Process each photo in turn...
    //$('#rotated').each(function (index) { })
    // Make the photo rotatable

    $('.rotated').mousedown(startRotate);

    // Start rotating an image

    $('.rotated').data('currentRotation', 0);

}

function startRotate(e) {
    //alert(111);

    // Exit if the shift key wasn't held down when the mouse button was pressed
    if (!e.shiftKey) return;

    // Track the image that we're going to rotate
    imageBeingRotated = this;

    // Store the angle of the mouse at the start of the rotation, relative to the image centre
    var imageCentre = getImageCentre(imageBeingRotated);
    var mouseStartXFromCentre = e.pageX - imageCentre[0];
    var mouseStartYFromCentre = e.pageY - imageCentre[1];
    mouseStartAngle = Math.atan2(mouseStartYFromCentre, mouseStartXFromCentre);

    // Store the current rotation angle of the image at the start of the rotation
    imageStartAngle = $(imageBeingRotated).data('currentRotation');

    // Set up an event handler to rotate the image as the mouse is moved
    $(document).mousemove(rotateImage);

    return false;
}

function stopRotate(e) {

    // Exit if we're not rotating an image
    if (!imageBeingRotated) return;

    // Remove the event handler that tracked mouse movements during the rotation
    //$(document).unbind('mousemove');

    // Cancel the image rotation by setting imageBeingRotated back to false.
    // Do this in a short while - after the click event has fired -
    // to prevent the lightbox appearing once the Shift key is released.
    setTimeout(function () { imageBeingRotated = false; }, 10);
    return false;
}

function rotateImage(e) {

    // Exit if we're not rotating an image
    if (!e.shiftKey) return;
    if (!imageBeingRotated) return;

    // Calculate the new mouse angle relative to the image centre
    var imageCentre = getImageCentre(imageBeingRotated);
    var mouseXFromCentre = e.pageX - imageCentre[0];
    var mouseYFromCentre = e.pageY - imageCentre[1];

    // alert(mouseXFromCentre);
    // alert(mouseYFromCentre);

    // var mouseXFromCentre = imageCentre[0];
    // var mouseYFromCentre = imageCentre[1];
    var mouseAngle = Math.atan2(mouseYFromCentre, mouseXFromCentre);

    // Calculate the new rotation angle for the image
    var rotateAngle = mouseAngle - mouseStartAngle + imageStartAngle;


    //alert('translate(880,580) rotate(' + rotateAngle + 'rad)')

    // Rotate the image to the new angle, and store the new angle

    console.log(imageBeingRotated);
    //$(imageBeingRotated).css('transform', 'rotate(' + rotateAngle + 'rad)');
    $(imageBeingRotated).attr('transform', 'translate(880,480) rotate(' + rotateAngle / Math.PI * 360 + ',0,0)');


    // $(imageBeingRotated).css('transform', 'translate(880,580)');
    // $(imageBeingRotated).css('-moz-transform', 'rotate(' + rotateAngle + 'rad)');
    // $(imageBeingRotated).css('-webkit-transform', 'rotate(' + rotateAngle + 'rad)');
    // $(imageBeingRotated).css('-o-transform', 'rotate(' + rotateAngle + 'rad)');

    //$(imageBeingRotated).attr('style', 'transform:translate(880,580) rotate(' + rotateAngle + 'rad);');

    //style="transform: rotate(0.352443rad);"
    //style="transform:translate(880,580) rotate(0.17855447625579696rad);"

    //$(imageBeingRotated).attr('transform', 'translate(880,580) rotate(' + rotateAngle + 'rad)');

    //console.log(rotateAngle);

    $(imageBeingRotated).data('currentRotation', rotateAngle);
    return false;


}


function getImageCentre(image) {

    // Rotate the image to 0 radians
    // $(image).css('transform', 'translate(880,580) rotate(0rad)');
    // $(image).css('-moz-transform', 'translate(880,580) rotate(0rad)');
    // $(image).css('-webkit-transform', 'translate(880,580) rotate(0rad)');
    // $(image).css('-o-transform', 'translate(880,580) rotate(0rad)');

    // Measure the image centre
    var imageOffset = $(image).offset();
    var imageCentreX = imageOffset.left + $(image).width() / 2;
    var imageCentreY = imageOffset.top + $(image).height() / 2;

    // Rotate the image back to its previous angle
    var currentRotation = $(image).data('currentRotation');
    // $(imageBeingRotated).css('transform', 'translate(880,580) rotate(' + currentRotation + 'rad)');
    // $(imageBeingRotated).css('-moz-transform', 'translate(880,580) rotate(' + currentRotation + 'rad)');
    // $(imageBeingRotated).css('-webkit-transform', 'translate(880,580) rotate(' + currentRotation + 'rad)');
    // $(imageBeingRotated).css('-o-transform', 'translate(880,580) rotate(' + currentRotation + 'rad)');

    // Return the calculated centre coordinates
    // alert(imageCentreX);
    // alert(imageCentreY);
    return Array(imageCentreX, imageCentreY);
}