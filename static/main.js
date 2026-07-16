var selectedLang = null;
var isListening = false;
var recognition = null;
var isSpeaking = false;
var msgCounter = 0;

var TRANSLATE_LANGS = [
  {code: 'yo', label: 'Yoruba'},
  {code: 'ig', label: 'Igbo'},
  {code: 'ha', label: 'Hausa'},
  {code: 'en', label: 'English'},
  {code: 'fr', label: 'French'},
  {code: 'ar', label: 'Arabic'},
  {code: 'pt', label: 'Pidgin'}
];

function setLang(lang) {
  selectedLang = lang;
  document.getElementById('btn-en').className = 'lang-btn' + (lang === 'english' ? ' active' : '');
  document.getElementById('btn-ha').className = 'lang-btn' + (lang === 'hausa' ? ' active' : '');
  var enChips = document.querySelectorAll('.en-chip');
  var haChips = document.querySelectorAll('.ha-chip');
  for (var i = 0; i < enChips.length; i++) enChips[i].style.display = lang === 'hausa' ? 'none' : '';
  for (var i = 0; i < haChips.length; i++) haChips[i].style.display = lang === 'hausa' ? '' : 'none';
  var input = document.getElementById('userInput');
  if (lang === 'hausa') {
    input.placeholder = 'Ka bayyana abin da ya faru...';
    document.getElementById('heroTitle').textContent = 'Kana da sako ko kira mai damuwa?';
    document.getElementById('heroSub').textContent = 'Ka bayyana abin da ya faru kuma OGA_WATCHAFRI zai gano zamba, ba da shawara, kuma ya koya maka yadda za ka kare kanka.';
  } else {
    input.placeholder = 'Describe the suspicious message, call, or situation...';
    document.getElementById('heroTitle').textContent = 'Got a suspicious message, call, or situation?';
    document.getElementById('heroSub').textContent = 'Describe what happened and OGA_WATCHAFRI will detect the fraud, advise you on what to do, and teach you how to stay safe in plain language.';
  }
}

function toggleVoice() {
  if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
    alert('Voice input is not supported in your browser. Please use Chrome or Edge.');
    return;
  }
  if (isListening) { stopListening(); } else { startListening(); }
}

function startListening() {
  var SR = window.SpeechRecognition || window.webkitSpeechRecognition;
  recognition = new SR();
  recognition.continuous = false;
  recognition.interimResults = true;
  recognition.lang = selectedLang === 'hausa' ? 'ha-NG' : 'en-NG';
  recognition.onstart = function() {
    isListening = true;
    document.getElementById('micBtn').className = 'mic-btn listening';
    document.getElementById('micBtn').textContent = 'Stop';
    document.getElementById('userInput').placeholder = selectedLang === 'hausa' ? 'Ina sauraro...' : 'Listening...';
  };
  recognition.onresult = function(e) {
    var t = '';
    for (var i = e.resultIndex; i < e.results.length; i++) t += e.results[i][0].transcript;
    document.getElementById('userInput').value = t;
    autoResize(document.getElementById('userInput'));
  };
  recognition.onend = function() {
    stopListening();
    var t = document.getElementById('userInput').value.trim();
    if (t) sendMessage();
  };
  recognition.onerror = function(e) { stopListening(); };
  recognition.start();
}

function stopListening() {
  isListening = false;
  if (recognition) recognition.stop();
  var btn = document.getElementById('micBtn');
  btn.className = 'mic-btn';
  btn.textContent = 'Mic';
  document.getElementById('userInput').placeholder = selectedLang === 'hausa' ? 'Ka bayyana abin da ya faru...' : 'Describe the suspicious message, call, or situation...';
}

function speakText(btnId, lang) {
  var btn = document.getElementById(btnId);
  if (!btn) return;
  var encoded = btn.getAttribute('data-speech');
  if (!encoded) return;
  var text = '';
  try { text = decodeURIComponent(escape(atob(encoded))); } catch(e) { text = encoded; }
  if (isSpeaking) {
    window.speechSynthesis.cancel();
    isSpeaking = false;
    btn.className = 'action-btn';
    btn.textContent = lang === 'hausa' ? 'Karanta' : 'Listen';
    return;
  }
  var u = new SpeechSynthesisUtterance(text);
  u.lang = lang === 'hausa' ? 'ha' : 'en-NG';
  u.rate = 0.9;
  isSpeaking = true;
  btn.className = 'action-btn speaking';
  btn.textContent = lang === 'hausa' ? 'Tsaya' : 'Stop';
  u.onend = function() {
    isSpeaking = false;
    btn.className = 'action-btn';
    btn.textContent = lang === 'hausa' ? 'Karanta' : 'Listen';
  };
  window.speechSynthesis.speak(u);
}

function toggleTranslatePanel(panelId) {
  var p = document.getElementById(panelId);
  if (!p) return;
  p.style.display = p.style.display === 'block' ? 'none' : 'block';
}

function handleTranslate(el) {
  var langCode = el.getAttribute('data-lang');
  var encoded = el.getAttribute('data-encoded');
  var outputId = el.getAttribute('data-output');
  var panelId = el.getAttribute('data-panel');
  var rawText = '';
  try { rawText = decodeURIComponent(escape(atob(encoded))); } catch(e) { rawText = ''; }

  var panel = document.getElementById(panelId);
  if (panel) {
    var btns = panel.querySelectorAll('.lang-option');
    for (var i = 0; i < btns.length; i++) btns[i].className = 'lang-option';
  }
  el.className = 'lang-option selected';

  var out = document.getElementById(outputId);
  if (!out) return;
  out.textContent = 'Translating...';
  out.style.color = 'var(--m)';
  out.style.display = 'block';

  var clean = rawText.substring(0, 400);
  var url = 'https://api.mymemory.translated.net/get?q=' + encodeURIComponent(clean) + '&langpair=en|' + langCode;

  fetch(url)
    .then(function(r) { return r.json(); })
    .then(function(d) {
      if (d.responseStatus === 200 && d.responseData && d.responseData.translatedText) {
        out.textContent = d.responseData.translatedText;
        out.style.color = 'var(--t)';
      } else {
        out.textContent = 'Translation limit reached. Please try again in a moment.';
        out.style.color = 'var(--r)';
      }
    })
    .catch(function() {
      out.textContent = 'Translation unavailable. Please check your connection.';
      out.style.color = 'var(--r)';
    });
}

function autoResize(el) { el.style.height = 'auto'; el.style.height = Math.min(el.scrollHeight, 120) + 'px'; }
function handleKey(e) { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); sendMessage(); } }
function useExample(el) { document.getElementById('userInput').value = el.textContent; sendMessage(); }

function addMessage(role, content) {
  var c = document.getElementById('chatContainer');
  var d = document.createElement('div');
  d.className = 'message ' + role;
  var av = role === 'user' ? 'You' : 'OGA';
  d.innerHTML = '<div class="avatar ' + (role === 'user' ? 'user' : 'bot') + '">' + av + '</div><div class="bubble">' + content + '</div>';
  c.appendChild(d);
  d.scrollIntoView({behavior: 'smooth', block: 'end'});
  return d.querySelector('.bubble');
}

function showTyping() {
  var c = document.getElementById('chatContainer');
  var d = document.createElement('div');
  d.className = 'message bot'; d.id = 'typing-indicator';
  d.innerHTML = '<div class="avatar bot">OGA</div><div class="bubble"><div class="typing"><span></span><span></span><span></span></div></div>';
  c.appendChild(d);
  d.scrollIntoView({behavior: 'smooth', block: 'end'});
}
function removeTyping() { var el = document.getElementById('typing-indicator'); if (el) el.remove(); }

function safeEncode(text) {
  try { return btoa(unescape(encodeURIComponent(text))); }
  catch(e) { return btoa(text.replace(/[^\x00-\x7F]/g, '?')); }
}

function formatResponse(data, msgId) {
  var det = data.detection || {};
  var sev = (det.severity || 'medium').toLowerCase();
  var fraudType = (det.fraud_type || 'Unknown').replace(/</g,'&lt;').replace(/>/g,'&gt;');
  var redFlags = (det.red_flags || []).map(function(f) {
    return '<div style="margin:3px 0;font-size:13px;">&#9888; ' + f.replace(/</g,'&lt;').replace(/>/g,'&gt;') + '</div>';
  }).join('');
  var reasoning = (det.reasoning || '').replace(/</g,'&lt;').replace(/>/g,'&gt;');
  var advice = (data.incident_advice || '').replace(/</g,'&lt;').replace(/>/g,'&gt;');
  var education = (data.education || '').replace(/</g,'&lt;').replace(/>/g,'&gt;');
  var lang = data.language || 'english';
  var panelId = 'tp-' + msgId;
  var outputId = 'to-' + msgId;
  var speakId = 'sp-' + msgId;
  var rawForTranslation = (data.incident_advice || '') + ' ' + (data.education || '');
  var encodedText = safeEncode(rawForTranslation);
  var encodedSpeech = safeEncode((det.fraud_type || '') + '. ' + (det.reasoning || '') + '. ' + (data.incident_advice || ''));

  var langBtns = TRANSLATE_LANGS
    .filter(function(l) {
      return !(l.code === 'ha' && lang === 'hausa') && !(l.code === 'en' && lang === 'english');
    })
    .map(function(l) {
      var btnId = 'lb-' + msgId + '-' + l.code;
      return '<div class="lang-option" id="' + btnId + '" data-lang="' + l.code + '" data-encoded="' + encodedText + '" data-output="' + outputId + '" data-panel="' + panelId + '" onclick="handleTranslate(this)">' + l.label + '</div>';
    }).join('');

  var n1 = lang === 'hausa' ? 'NODE 1 - GANO ZAMBA' : 'Node 1 - Fraud Detector';
  var n2 = lang === 'hausa' ? 'NODE 2 - SHAWARA' : 'Node 2 - Incident Advisor';
  var n3 = lang === 'hausa' ? 'NODE 3 - ILIMI' : 'Node 3 - Awareness Educator';
  var listenLbl = lang === 'hausa' ? 'Karanta' : 'Listen';
  var transLbl = lang === 'hausa' ? 'Fassara' : 'Translate';
  var transTitle = lang === 'hausa' ? 'Zabi harshe:' : 'Translate to:';
  var doneLbl = lang === 'hausa' ? 'Bincike ya kare. Kare kanka!' : 'Analysis complete. Stay safe!';

  return '<div style="font-weight:600;font-size:15px;margin-bottom:12px;">'
    + (lang === 'hausa' ? 'OGA_WATCHAFRI ya bincika yanayin ka:' : 'OGA_WATCHAFRI has analyzed your situation:')
    + '</div>'
    + '<div class="node-section node-detect">'
    + '<div class="node-title">' + n1 + '</div>'
    + '<div style="font-weight:600;font-size:14px;">' + fraudType
    + ' <span class="badge ' + sev + '">' + (det.severity || '').toUpperCase() + '</span>'
    + ' <span class="badge" style="background:rgba(255,255,255,.1);color:var(--m)">' + (det.confidence || '') + ' confidence</span></div>'
    + (redFlags ? '<div style="margin-top:8px;">' + redFlags + '</div>' : '')
    + (reasoning ? '<div style="margin-top:8px;font-size:12px;color:var(--m);font-style:italic;">' + reasoning + '</div>' : '')
    + '</div>'
    + '<div class="node-section node-advise" style="margin-top:10px;">'
    + '<div class="node-title">' + n2 + '</div>'
    + '<pre>' + advice + '</pre>'
    + '</div>'
    + '<div class="node-section node-educate" style="margin-top:10px;">'
    + '<div class="node-title">' + n3 + '</div>'
    + '<pre>' + education + '</pre>'
    + '</div>'
    + '<div class="response-actions">'
    + '<button class="action-btn" id="' + speakId + '" data-speech="' + encodedSpeech + '" onclick="speakText(\'' + speakId + '\',\'' + lang + '\')">' + listenLbl + '</button>'
    + '<button class="action-btn" onclick="toggleTranslatePanel(\'' + panelId + '\')">' + transLbl + '</button>'
    + '</div>'
    + '<div class="translate-panel" id="' + panelId + '" style="display:none;">'
    + '<h4>' + transTitle + '</h4>'
    + '<div class="lang-grid">' + langBtns + '</div>'
    + '<div class="translated-output" id="' + outputId + '"></div>'
    + '</div>'
    + '<div style="margin-top:12px;font-size:12px;color:var(--m);text-align:center;font-family:DM Mono,monospace;">&#9989; ' + doneLbl + ' &#127758;</div>';
}

function sendMessage() {
  var input = document.getElementById('userInput');
  var btn = document.getElementById('sendBtn');
  var situation = input.value.trim();
  if (!situation) return;
  addMessage('user', situation);
  input.value = ''; input.style.height = 'auto';
  btn.disabled = true; showTyping();
  fetch('/api/analyze', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({situation: situation, language: selectedLang})
  })
  .then(function(r) { return r.json(); })
  .then(function(data) {
    removeTyping();
    msgCounter++;
    if (data.error) {
      addMessage('bot', '<span style="color:var(--r)">Error: ' + data.error + '</span>');
    } else {
      addMessage('bot', formatResponse(data, msgCounter));
    }
    btn.disabled = false;
  })
  .catch(function() {
    removeTyping();
    addMessage('bot', '<span style="color:var(--r)">Something went wrong. Please try again.</span>');
    btn.disabled = false;
  });
}
