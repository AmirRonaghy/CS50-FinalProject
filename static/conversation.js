// JavaScript to dynamically display character and student dialog without reloading page
// Use jQuery and Ajax to send data to conversation endpoint via post request
// Guidance and instructions taken from the following sources:
// Create a Deep Learning Machine Learning Chatbot with Python and Flask -- https://www.youtube.com/watch?v=8HifpykuTI4&t=20s
// How to create a Messenger Style Chat Bot with JavaScript Tutorial (Part 2) -- https://www.youtube.com/watch?v=g9SewnLpTE0
// Submit AJAX Forms with jQuery and Flask -- https://www.youtube.com/watch?v=IZWtHsM3Y5A
// Flask form submission without Page Reload -- https://www.geeksforgeeks.org/flask-form-submission-without-page-reload/


// Store chat textbox and student audio elements in variable for reference across functions
var input = document.getElementById("textInput");
var studentAudioID = document.getElementById('student-speech');

// Function to load new student speech audio file
function addStudentAudio(file) {
  var source = document.getElementById('student-source');
  source.src = "/static/" + file;
  source.type= "audio/mpeg";
  studentAudioID.load();
}

// Function to load new character speech audio file after student speech audio has played
function addCharAudio(file) {
  var audio = document.getElementById('character-speech');
  var source = document.getElementById('character-source');
  source.src = "/static/" + file;
  source.type= "audio/mpeg";
  studentAudioID.addEventListener('ended', (event) => {
    setTimeout(function() {
      audio.load();
    }, 2000);
  });
}

// Function to activate chat and TTS audio when user presses enter
input.addEventListener("keyup", function(event) {
  if (event.keyCode === 13) {
   event.preventDefault();
   document.getElementById("sendButton").click();
  }
});

// Function to display dialog text in formatted HTML
// If character dialog, display only after student speech audio has played
function addInput(originalInput, translatedInput, inputClass) {
  let dialogHtml = "<p class=" + inputClass + "><span>" + originalInput + "<br>" +
  "<br>" + translatedInput + "</span></p>";
  $("#chatbox").append(dialogHtml);
  input.value = "";
  document.getElementById("chat-bar-bottom").scrollIntoView(true);
}

// Function to send student dialog to conversation end point via Ajax request
// Send chatbot response, translations and translated speech to HTML via JSON object returned by Python function
// Convert translated text to speech
function getTranslations() {
  return $.ajax({
      type: "POST",
      url: "/conversation",
      data: {
        student: $("#textInput").val(),
      },
      success: function(result) {
        let studentText = input.value;
        let studentTranslated = result.studentTranslated;
        let studentAudio = result.studentAudio;
        let characterText = result.character;
        let characterTranslated = result.characterTranslated;
        let characterAudio = result.characterAudio;
        addInput(studentText, studentTranslated, "studentText");
        addStudentAudio(studentAudio);
        addInput(characterText, characterTranslated, "botText");
        addCharAudio(characterAudio);
      },
      error: function(result) {
          alert("error");
    }
  });
}

// Display translated dialog on HTML page, play speech audio and clear text box when send button is clicked
jQuery(document).ready(function() {
  $("#sendButton").click(function(e) {
    e.preventDefault();
    getTranslations();
  });
});

// Speech recognition to be activated when student clicks microphone microphone button
if ("webkitSpeechRecognition" in window) {
  let speechRecognition = new webkitSpeechRecognition();
  let mic = document.getElementById("micButton");
  let listening = false;
  speechRecognition.continuous = true;
  speechRecognition.interimResults = false;

  speechRecognition.onresult = (event) => {
    let final_transcript = "";
    for (let i = event.resultIndex; i < event.results.length; ++i) {
      if (event.results[i].isFinal) {
        final_transcript += event.results[i][0].transcript;
      }
    document.getElementById("textInput").value = final_transcript;
    document.getElementById("sendButton").click();
    };
  };


  mic.onclick = () => {
    if (!listening) {
      speechRecognition.start();
      mic.style.color = "lightblue";
      listening = true;
    }
    else {
      speechRecognition.stop();
      mic.style.color = "blue";
      listening = false;
    };
  };

}
else {
  console.log("Speech Recognition Not Available");
};

// Prompt user for permission to use device microphone
// https://developer.mozilla.org/en-US/docs/Web/API/WebRTC_API/Build_a_phone_with_peerjs/Connect_peers/Get_microphone_permission
function getLocalStream() {
    navigator.mediaDevices.getUserMedia({video: false, audio: true}).then( stream => {
        window.localStream = stream;
        window.localAudio.srcObject = stream;
        window.localAudio.autoplay = true;
    }).catch( err => {
        console.log("u got an error:" + err)
    });
}

getLocalStream();
