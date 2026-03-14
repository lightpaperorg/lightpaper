/* Browser-native text-to-speech for lightpaper.org documents */
(function () {
  var btn = document.getElementById("listen-btn");
  if (!btn || !window.speechSynthesis) {
    if (btn) btn.style.display = "none";
    return;
  }

  var synth = window.speechSynthesis;
  var playing = false;
  var paused = false;

  btn.addEventListener("click", function () {
    if (playing && !paused) {
      synth.pause();
      paused = true;
      btn.textContent = "Resume";
      return;
    }
    if (paused) {
      synth.resume();
      paused = false;
      btn.textContent = "Pause";
      return;
    }

    var article = document.querySelector("article");
    if (!article) return;

    var text = article.innerText || article.textContent;

    /* Speech synthesis has a ~32K char limit on some browsers.
       Split into chunks at sentence boundaries. */
    var chunks = [];
    var maxLen = 4000;
    var remaining = text;
    while (remaining.length > 0) {
      if (remaining.length <= maxLen) {
        chunks.push(remaining);
        break;
      }
      var cut = remaining.lastIndexOf(". ", maxLen);
      if (cut < maxLen / 2) cut = remaining.lastIndexOf(" ", maxLen);
      if (cut < maxLen / 2) cut = maxLen;
      chunks.push(remaining.slice(0, cut + 1));
      remaining = remaining.slice(cut + 1);
    }

    var idx = 0;

    function speakNext() {
      if (idx >= chunks.length) {
        playing = false;
        paused = false;
        btn.textContent = "Listen";
        return;
      }
      var utt = new SpeechSynthesisUtterance(chunks[idx]);
      utt.rate = 1.0;
      utt.onend = function () {
        idx++;
        speakNext();
      };
      utt.onerror = function () {
        playing = false;
        paused = false;
        btn.textContent = "Listen";
      };
      synth.speak(utt);
    }

    synth.cancel();
    playing = true;
    paused = false;
    btn.textContent = "Pause";
    speakNext();
  });

  /* Reset if synthesis ends externally */
  window.addEventListener("beforeunload", function () {
    synth.cancel();
  });
})();
