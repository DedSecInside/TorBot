
var slider = document.getElementById("myRange");
var output = document.getElementById("depth");
output.innerHTML = slider.value;

slider.oninput = function() {
  output.innerHTML = this.value;
}
