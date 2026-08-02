var selectedLang = null;
var isListening = false;
var recognition = null;
var isSpeaking = false;
var msgCounter = 0;

// Language codes used by the MyMemory translate API for each UI language
var LANG_CODES = { english: 'en', hausa: 'ha', yoruba: 'yo', igbo: 'ig', pidgin: 'pcm' };

// 'pt' (Portuguese) was previously mislabeled as "Pidgin" - fixed to 'pcm', the real
// ISO code for Nigerian Pidgin. Yoruba/Igbo removed from this list since they are now
// full UI languages (selectable via the top toggle) rather than translate-only targets.
// 'pcm' (Nigerian Pidgin) removed from this list - MyMemory only supports ISO
// 639-1 codes and has no valid code for Pidgin, so every request failed.
// Pidgin is now a full UI/AI language instead (see UI_STRINGS.pidgin below).
var TRANSLATE_LANGS = [
  {code: 'ha', label: 'Hausa'},
  {code: 'en', label: 'English'},
  {code: 'yo', label: 'Yoruba'},
  {code: 'ig', label: 'Igbo'},
  {code: 'fr', label: 'French'},
  {code: 'ar', label: 'Arabic'}
];

// All UI chrome text for each supported language, in one place.
var UI_STRINGS = {
  english: {
    intro: 'OGA_WATCHAFRI has analyzed your situation:',
    placeholder: 'Describe the suspicious message, call, or situation...',
    heroTitle: 'Got a suspicious message, call, or situation?',
    heroSub: 'Describe what happened and OGA_WATCHAFRI will detect the fraud, advise you on what to do, and teach you how to stay safe in plain language.',
    node1: 'Node 1 - Fraud Detector',
    node2: 'Node 2 - Incident Advisor',
    node3: 'Node 3 - Awareness Educator',
    listen: 'Listen',
    translate: 'Translate',
    translateTo: 'Translate to:',
    done: 'Analysis complete. Stay safe!',
    communityAlert: 'Community Alert: reported {n} times by other users before you.',
    callEfcc: 'Call EFCC Now',
    alertFamily: 'Alert Family on WhatsApp',
    copyReport: 'Copy Report for EFCC',
    copied: 'Copied!',
    whatsappTemplate: '*OGA_WATCHAFRI Fraud Alert*\n\nType: {fraudType}\n\n{reasoning}\n\nBe careful - do not share OTPs or send money. Report to EFCC: 0800-326-5252',
    reportTemplate: 'FRAUD REPORT (via OGA_WATCHAFRI)\nType: {fraudType}\nSeverity: {severity}\nRed flags: {redFlags}\nDetails: {reasoning}\nEFCC Hotline: 0800-326-5252'
  },
  hausa: {
    intro: 'OGA_WATCHAFRI ya bincika yanayin ka:',
    placeholder: 'Ka bayyana abin da ya faru...',
    heroTitle: 'Kana da sako ko kira mai damuwa?',
    heroSub: 'Ka bayyana abin da ya faru kuma OGA_WATCHAFRI zai gano zamba, ba da shawara, kuma ya koya maka yadda za ka kare kanka.',
    node1: 'NODE 1 - GANO ZAMBA',
    node2: 'NODE 2 - SHAWARA',
    node3: 'NODE 3 - ILIMI',
    listen: 'Karanta',
    translate: 'Fassara',
    translateTo: 'Zabi harshe:',
    done: 'Bincike ya kare. Kare kanka!',
    communityAlert: 'Sanarwar Al\'umma: an ba da rahoto {n} sau daga wasu masu amfani.',
    callEfcc: 'Kira EFCC Yanzu',
    alertFamily: 'Sanar da Iyali a WhatsApp',
    copyReport: 'Kwafi Rahoto don EFCC',
    copied: 'An kwafa!',
    whatsappTemplate: '*Sanarwar Zamba ta OGA_WATCHAFRI*\n\nIri: {fraudType}\n\n{reasoning}\n\nKa yi hankali - kada ka baiwa kowa OTP ko ka aika kudi. Ka bayar da rahoto ga EFCC: 0800-326-5252',
    reportTemplate: 'RAHOTON ZAMBA (ta OGA_WATCHAFRI)\nIri: {fraudType}\nMatakin hadari: {severity}\nAlamun hadari: {redFlags}\nBayani: {reasoning}\nLambar EFCC: 0800-326-5252'
  },
  yoruba: {
    intro: 'OGA_WATCHAFRI ti ṣàyẹ̀wò ipò rẹ:',
    placeholder: "Ṣàlàyé ifiranṣẹ ifura, ipè, tabi ipo náà...",
    heroTitle: "Ṣe o ti gba ifiranṣẹ ifura, ipè, tabi ipo ajeji kan?",
    heroSub: "Ṣàlàyé ohun tí ó ṣẹlẹ̀, OGA_WATCHAFRI yóò sì ṣàwárí jìbìtì náà, fún ọ ní ìmọ̀ràn nípa ohun tí o gbọ́dọ̀ ṣe, kí ó sì kọ́ ọ bí o ṣe lè dáàbò bo ara rẹ ní èdè tí ó rọrùn.",
    node1: 'APA 1 - AWARI JIBITI',
    node2: 'APA 2 - IMORAN',
    node3: 'APA 3 - EKO',
    listen: 'Gbọ́',
    translate: 'Túmọ̀',
    translateTo: 'Túmọ̀ sí:',
    done: 'Ìtúpalẹ̀ ti parí. Dáàbò bo ara rẹ!',
    communityAlert: "Ìkìlọ̀ Àdúgbò: a ti fi ìròyìn yìí ránṣẹ́ ní ìgbà {n} láti ọ̀dọ̀ àwọn oníbàárà mìíràn.",
    callEfcc: 'Pe EFCC Nísisìyí',
    alertFamily: 'Kìlọ̀ Fún Ẹbí Lórí WhatsApp',
    copyReport: 'Da Ìròyìn Kọ fún EFCC',
    copied: 'Ti dà kọ!',
    whatsappTemplate: "*Ìkìlọ̀ Jìbìtì láti ọ̀dọ̀ OGA_WATCHAFRI*\n\nIrú: {fraudType}\n\n{reasoning}\n\nṢọ́ra - má ṣe fi OTP tàbí kí o fi owó ránṣẹ́ fún ẹnikẹ́ni. Fi ìròyìn ránṣẹ́ sí EFCC: 0800-326-5252",
    reportTemplate: 'ÌRÒYÌN JÌBÌTÍ (láti ọ̀dọ̀ OGA_WATCHAFRI)\nIrú: {fraudType}\nÌwọ̀n ewu: {severity}\nÀmì ewu: {redFlags}\nÀlàyé: {reasoning}\nNọ́mbà EFCC: 0800-326-5252'
  },
  igbo: {
    intro: 'OGA_WATCHAFRI enyochala ọnọdụ gị:',
    placeholder: 'Kọwaa ozi enyo, oku, ma ọ bụ ọnọdụ ahụ...',
    heroTitle: 'Ị nwetara ozi enyo, oku, ma ọ bụ ọnọdụ enyo?',
    heroSub: "Kọwaa ihe merenụ, OGA_WATCHAFRI ga-achọpụta aghụghọ ahụ, dụọ gị ọdụ ihe ị ga-eme, ma kụziere gị otu ị ga-esi nchekwa onwe gị n'asụsụ dị mfe.",
    node1: 'AKỤKỤ 1 - ACHỌPỤTA AGHỤGHỌ',
    node2: 'AKỤKỤ 2 - NDỤMỌDỤ',
    node3: 'AKỤKỤ 3 - MMỤTA',
    listen: 'Gee ntị',
    translate: 'Tụgharịa',
    translateTo: 'Tụgharịa gaa:',
    done: 'Nyocha agwụla. Chebe onwe gị!',
    communityAlert: "Ọkwa Obodo: e kọwo aghụghọ a ugboro {n} site n'aka ndị ọzọ.",
    callEfcc: 'Kpọọ EFCC Ugbu a',
    alertFamily: 'Dọọ Ezinụlọ Aka na WhatsApp',
    copyReport: 'Detuo Akụkọ maka EFCC',
    copied: 'Edetuola!',
    whatsappTemplate: "*Ọkwa Aghụghọ site na OGA_WATCHAFRI*\n\nỤdị: {fraudType}\n\n{reasoning}\n\n\nKpachara anya - ekwela ka i nye onye ọ bụla OTP ma ọ bụ zipu ego. Kọọ akụkọ nye EFCC: 0800-326-5252",
    reportTemplate: 'AKỤKỌ AGHỤGHỌ (site na OGA_WATCHAFRI)\nỤdị: {fraudType}\nỌkwa ihe egwu: {severity}\nAkara ize ndụ: {redFlags}\nNkọwa: {reasoning}\nNọmba EFCC: 0800-326-5252'
  },
  pidgin: {
    intro: 'OGA_WATCHAFRI don check your matter:',
    placeholder: 'Tell us wetin happen - message, call, or situation...',
    heroTitle: 'You get suspicious message, call, or situation?',
    heroSub: 'Tell us wetin happen and OGA_WATCHAFRI go detect di fraud, advise you wetin to do, and teach you how to stay safe for simple language.',
    node1: 'NODE 1 - DETECT FRAUD',
    node2: 'NODE 2 - ADVICE',
    node3: 'NODE 3 - LESSON',
    listen: 'Listen',
    translate: 'Translate',
    translateTo: 'Translate go:',
    done: "Analysis don finish. Stay safe!",
    communityAlert: 'Community Warning: people don report am {n} times before you.',
    callEfcc: 'Call EFCC Now',
    alertFamily: 'Warn Family for WhatsApp',
    copyReport: 'Copy Report for EFCC',
    copied: "E don copy!",
    whatsappTemplate: "*OGA_WATCHAFRI Fraud Warning*\n\nType: {fraudType}\n\n{reasoning}\n\nBe careful - no share OTP or send money. Report to EFCC: 0800-326-5252",
    reportTemplate: 'FRAUD REPORT (from OGA_WATCHAFRI)\nType: {fraudType}\nHow e serious: {severity}\nRed flags: {redFlags}\nDetails: {reasoning}\nEFCC Hotline: 0800-326-5252'
  }
};

var LANG_BUTTON_IDS = {
  english: 'btn-en',
  hausa: 'btn-ha',
  yoruba: 'btn-yo',
  igbo: 'btn-ig',
  pidgin: 'btn-pi'
};

var LANG_CHIP_CLASSES = {
  english: 'en-chip',
  hausa: 'ha-chip',
  yoruba: 'yo-chip',
  igbo: 'ig-chip',
  pidgin: 'pi-chip'
};

function setLang(lang) {
  selectedLang = lang;

  for (var key in LANG_BUTTON_IDS) {
    var btn = document.getElementById(LANG_BUTTON_IDS[key]);
    if (btn) btn.className = 'lang-btn' + (key === lang ? ' active' : '');
  }

  for (var key2 in LANG_CHIP_CLASSES) {
    var chips = document.querySelectorAll('.' + LANG_CHIP_CLASSES[key2]);
    for (var i = 0; i < chips.length; i++) chips[i].style.display = (key2 === lang) ? '' : 'none';
  }

  var strings = UI_STRINGS[lang] || UI_STRINGS.english;
  var input = document.getElementById('userInput');
  if (input) input.placeholder = strings.placeholder;
  var heroTitleEl = document.getElementById('heroTitle');
  if (heroTitleEl) heroTitleEl.textContent = strings.heroTitle;
  var heroSubEl = document.getElementById('heroSub');
  if (heroSubEl) heroSubEl.textContent = strings.heroSub;
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

function fallbackCopy(text) {
  var ta = document.createElement('textarea');
  ta.value = text;
  ta.style.position = 'fixed';
  ta.style.opacity = '0';
  document.body.appendChild(ta);
  ta.select();
  try { document.execCommand('copy'); } catch(e) {}
  document.body.removeChild(ta);
}

function copyReport(btn) {
  var encoded = btn.getAttribute('data-report');
  var text;
  try { text = decodeURIComponent(escape(atob(encoded))); } catch(e) { text = encoded; }
  var copiedLabel = btn.getAttribute('data-copied-label');
  var copyLabel = btn.getAttribute('data-copy-label');

  function showCopied() {
    btn.textContent = copiedLabel;
    setTimeout(function() { btn.textContent = '\uD83D\uDCCB ' + copyLabel; }, 2000);
  }

  if (navigator.clipboard && navigator.clipboard.writeText) {
    navigator.clipboard.writeText(text).then(showCopied).catch(function() {
      fallbackCopy(text);
      showCopied();
    });
  } else {
    fallbackCopy(text);
    showCopied();
  }
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

  var currentCode = LANG_CODES[lang] || 'en';
  var langBtns = TRANSLATE_LANGS
    .filter(function(l) { return l.code !== currentCode; })
    .map(function(l) {
      var btnId = 'lb-' + msgId + '-' + l.code;
      return '<div class="lang-option" id="' + btnId + '" data-lang="' + l.code + '" data-encoded="' + encodedText + '" data-output="' + outputId + '" data-panel="' + panelId + '" onclick="handleTranslate(this)">' + l.label + '</div>';
    }).join('');

  var strings = UI_STRINGS[lang] || UI_STRINGS.english;
  var n1 = strings.node1;
  var n2 = strings.node2;
  var n3 = strings.node3;
  var listenLbl = strings.listen;
  var transLbl = strings.translate;
  var transTitle = strings.translateTo;
  var doneLbl = strings.done;

  var communityBanner = '';
  if (data.community_alerts && data.community_alerts.length) {
    communityBanner = data.community_alerts.map(function(a) {
      var msg = strings.communityAlert.replace('{n}', a.report_count);
      return '<div class="community-alert">&#9888; ' + msg + '</div>';
    }).join('');
  }

  var escalation = '';
  if (sev === 'critical') {
    var waText = strings.whatsappTemplate
      .replace('{fraudType}', det.fraud_type || '')
      .replace('{reasoning}', det.reasoning || '');
    var waUrl = 'https://wa.me/?text=' + encodeURIComponent(waText);
    var reportText = strings.reportTemplate
      .replace('{fraudType}', det.fraud_type || '')
      .replace('{severity}', det.severity || '')
      .replace('{redFlags}', (det.red_flags || []).join('; '))
      .replace('{reasoning}', det.reasoning || '');
    var encodedReport = safeEncode(reportText);
    escalation = '<div class="escalation-actions">'
      + '<a class="action-btn escalate-btn" href="tel:08003265252">&#128222; ' + strings.callEfcc + '</a>'
      + '<a class="action-btn escalate-btn" href="' + waUrl + '" target="_blank" rel="noopener">&#128241; ' + strings.alertFamily + '</a>'
      + '<button class="action-btn escalate-btn" data-report="' + encodedReport + '" data-copied-label="' + strings.copied + '" data-copy-label="' + strings.copyReport + '" onclick="copyReport(this)">&#128203; ' + strings.copyReport + '</button>'
      + '</div>';
  }

  return '<div style="font-weight:600;font-size:15px;margin-bottom:12px;">'
    + strings.intro
    + '</div>'
    + communityBanner
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
    + escalation
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
