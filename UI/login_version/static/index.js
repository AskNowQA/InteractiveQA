
function appendText() {
    var txt1 = "<p>Text.</p>";               // Create element with HTML  
    var txt2 = $("<p></p>").text("Text.");   // Create with jQuery
    var txt3 = document.createElement("p");  // Create with DOM
    txt3.innerHTML = "Text.";
    $("div1").append(txt1, txt2, txt3);      // Append the new elements 
}
/*
var $newAccordion = $(
                        '<div class="panel panel-default" id ="accordion2">
                            <div class="panel-heading">
                                <h4 class="panel-title">
                                    <a data-toggle="collapse" data-parent="#accordion"
                                       href="#collapseTwo">
                                        <div id="questionDisplay2">
                                        </div>
                                    </a>
                                </h4>
                            </div>
                            <div id="collapseTwo" class="panel-collapse collapse collapse">
                                <div class="panel-body">
                                    <button id="directAnswer3" type="button"></button>
                                    <button id="directAnswer4" type="button"></button>
                                    <button class="directAnswer" type="button">Skip</button>
                                </div>
                            </div>
                        </div>'
                        )
function addAcco(){
    alert("hello")
}
*/
