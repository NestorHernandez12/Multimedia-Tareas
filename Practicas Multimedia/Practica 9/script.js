function listen() {
  let inputArea = document.getElementById('input-area')
  let outputArea = document.getElementById('output-area')

  var recognition = new webkitSpeechRecognition();
  recognition.lang = "es-ES"; // Voz en español
  recognition.start();

  recognition.onresult = function(event) {
    let transcript = event.results[0][0].transcript.toLowerCase();

    inputArea.innerHTML = transcript;

    if (transcript.includes("hola")) {
      outputArea.innerHTML = "Hola usuario 👋";

    } else if (transcript.includes("clima")) {
      outputArea.innerHTML = "Clima en la pantalla";
      window.open("https://www.google.com/search?q=clima");

    } else if (transcript.includes("profesor")) {
      outputArea.innerHTML = "¿Qué necesitas jefe?";

    } else if (transcript.includes("canción") || transcript.includes("musica")) {
      outputArea.innerHTML = "Cancion lista!";
      window.open("https://www.youtube.com/watch?v=d2Tu9ctifx4");

    } else if (transcript.includes("reloj")) {
      
      let ahora = new Date();
      let hora = ahora.getHours();
      let minutos = ahora.getMinutes();

      if(minutos < 10){
        minutos = "0" + minutos;
      }

      outputArea.innerHTML = "La hora actual es: " + hora + ":" + minutos + " 🕒";

    } else {
      outputArea.innerHTML = "No entendí lo que dijiste 🤔";
    }
  }
}