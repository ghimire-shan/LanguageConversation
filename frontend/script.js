document.addEventListener('DOMContentLoaded', () => {

    // ================= NAVIGATION LOGIC =================
    const navConvBtn = document.getElementById('nav-conv-btn');
    const navPracBtn = document.getElementById('nav-prac-btn');
    const navIndicator = document.getElementById('nav-indicator');
    const conversationView = document.getElementById('conversation-view');
    const practiceView = document.getElementById('practice-view');

    function switchToConversation() {
        navConvBtn.classList.replace('text-slate-400', 'text-slate-800');
        navPracBtn.classList.replace('text-slate-800', 'text-slate-400');
        navIndicator.style.transform = 'translateX(0%)';
        
        conversationView.classList.add('active-view');
        conversationView.classList.remove('hidden-view');
        practiceView.classList.remove('active-view');
        practiceView.classList.add('hidden-view');
    }

    function switchToPractice() {
        navPracBtn.classList.replace('text-slate-400', 'text-slate-800');
        navConvBtn.classList.replace('text-slate-800', 'text-slate-400');
        navIndicator.style.transform = 'translateX(100%)';
        
        practiceView.classList.add('active-view');
        practiceView.classList.remove('hidden-view');
        conversationView.classList.remove('active-view');
        conversationView.classList.add('hidden-view');
    }

    navConvBtn.addEventListener('click', switchToConversation);
    navPracBtn.addEventListener('click', switchToPractice);


    // ================= CONVERSATION MODE LOGIC =================
    const convMicBtn = document.getElementById('conv-mic-btn');
    const convMicIcon = document.getElementById('conv-mic-icon');
    const convMicText = document.getElementById('conv-mic-text');
    const convMicSubtext = document.getElementById('conv-mic-subtext');
    const convVoiceBars = document.getElementById('conv-voice-bars');
    const convBtnBg = document.getElementById('conv-btn-bg');
    const convClearBtn = document.getElementById('conv-clear-btn');
    const historySource = document.getElementById('history-source');
    const historyTarget = document.getElementById('history-target');
    const convLangSelect = document.getElementById('conv-lang-select');
    const convLangSummary = document.getElementById('conv-lang-summary');
    const targetLabel = document.getElementById('target-label');

    let isConvMicActive = false;
    let demoPhraseIndex = 0;
    const demoPhrases = [
        { en: "Hello, how are you?", es: "Hola, ¿cómo estás?", fr: "Bonjour, comment allez-vous ?" },
        { en: "Where is the bathroom?", es: "¿Dónde está el baño?", fr: "Où sont les toilettes ?" },
        { en: "A coffee, please.", es: "Un café, por favor.", fr: "Un café, s'il vous plaît." }
    ];

    function updateConvLanguageUI() {
        const targetLangName = convLangSelect.options[convLangSelect.selectedIndex].text.split(' ')[0];
        convLangSummary.innerHTML = `English <span class="mx-2 text-blue-300">→</span> <span class="font-black text-teal-600">${targetLangName}</span>`;
        targetLabel.textContent = `Translation (${targetLangName})`;
    }

    function handleConvMicToggle() {
        isConvMicActive = !isConvMicActive;
        if (isConvMicActive) {
            convMicBtn.classList.remove('bg-slate-800');
            convBtnBg.classList.remove('opacity-0'); convBtnBg.classList.add('opacity-100');
            convMicIcon.classList.remove('bg-slate-600/80'); convMicIcon.classList.add('bg-white/30', 'scale-105');
            convMicText.textContent = "Listening..."; convMicSubtext.textContent = "Speak clearly";
            convVoiceBars.classList.add('animate-voice');
            Array.from(convVoiceBars.children).forEach(bar => { bar.classList.remove('opacity-30'); bar.classList.add('bg-gradient-to-t', 'from-blue-500', 'to-teal-400'); });
        } else {
            convMicBtn.classList.add('bg-slate-800');
            convBtnBg.classList.remove('opacity-100'); convBtnBg.classList.add('opacity-0');
            convMicIcon.classList.add('bg-slate-600/80'); convMicIcon.classList.remove('bg-white/30', 'scale-110');
            convMicText.textContent = "Tap to speak"; convMicSubtext.textContent = "Visual demo only";
            convVoiceBars.classList.remove('animate-voice');
            Array.from(convVoiceBars.children).forEach(bar => { bar.classList.add('opacity-30'); bar.classList.remove('bg-gradient-to-t', 'from-blue-500', 'to-teal-400'); });
            sendDemoMessage();
        }
    }

    function sendDemoMessage() {
        const phraseData = demoPhrases[demoPhraseIndex];
        const targetLangCode = convLangSelect.value;
        if (historySource.querySelector('.placeholder-text')) historySource.querySelector('.placeholder-text').remove();
        if (historyTarget.querySelector('.placeholder-text')) historyTarget.querySelector('.placeholder-text').remove();

        const sourceBubble = document.createElement('div');
        sourceBubble.className = "bg-white p-4 rounded-[1.2rem] rounded-tl-sm text-slate-700 font-bold shadow-sm animate-[fadeIn_0.3s_ease-out] border border-slate-50 text-base";
        sourceBubble.innerText = phraseData.en;
        historySource.appendChild(sourceBubble);

        const targetBubble = document.createElement('div');
        targetBubble.className = "bg-gradient-to-br from-teal-500 to-teal-600 p-4 rounded-[1.2rem] rounded-tl-sm text-white font-black shadow-lg shadow-teal-500/20 animate-[fadeIn_0.4s_ease-out] text-base";
        targetBubble.innerText = phraseData[targetLangCode];
        historyTarget.appendChild(targetBubble);

        historySource.scrollTop = historySource.scrollHeight;
        historyTarget.scrollTop = historyTarget.scrollHeight;
        demoPhraseIndex = (demoPhraseIndex + 1) % demoPhrases.length;
    }

    convMicBtn.addEventListener('click', handleConvMicToggle);
    convLangSelect.addEventListener('change', updateConvLanguageUI);
    convClearBtn.addEventListener('click', () => {
        historySource.innerHTML = '<p class="placeholder-text text-slate-300 italic text-center font-medium text-base mt-8">Tap the mic & start speaking...</p>';
        historyTarget.innerHTML = '<p class="placeholder-text text-teal-800/30 italic text-center font-medium text-base mt-8">Translation appears here...</p>';
        demoPhraseIndex = 0;
    });


    // ================= NEW PRACTICE MODE FLOW LOGIC =================
    const pracMicBtn = document.getElementById('prac-mic-btn');
    const pracMicIcon = document.getElementById('prac-mic-icon');
    const pracMicText = document.getElementById('prac-mic-text');
    const pracMicSubtext = document.getElementById('prac-mic-subtext');
    const pracBtnBg = document.getElementById('prac-btn-bg');
    const pracVoiceBars = document.getElementById('prac-voice-bars');
    const practiceInputState = document.getElementById('practice-input-state');
    const practiceResultsState = document.getElementById('practice-results-state');
    const pracResetBtn = document.getElementById('prac-reset-btn');

    let isPracMicActive = false;

    function handlePracMicClick() {
        if (!isPracMicActive) {
            isPracMicActive = true;
            pracMicBtn.classList.remove('bg-indigo-600');
            pracBtnBg.classList.remove('opacity-0'); pracBtnBg.classList.add('opacity-100');
            pracMicIcon.classList.remove('bg-indigo-800/50'); pracMicIcon.classList.add('bg-white/30', 'scale-105');
            pracMicText.textContent = "Listening..."; pracMicSubtext.textContent = "Tap to finish";
            pracVoiceBars.classList.remove('opacity-0', 'scale-95'); pracVoiceBars.classList.add('animate-voice', 'scale-100');
        } else {
            isPracMicActive = false;
            practiceInputState.classList.add('opacity-0', '-translate-y-5', 'scale-95');
            setTimeout(() => {
                 practiceInputState.classList.add('hidden');
                 practiceResultsState.classList.remove('hidden');
                 setTimeout(() => {
                     practiceResultsState.classList.remove('opacity-0', 'scale-95');
                 }, 50);
            }, 300);
        }
    }

    function resetPractice() {
        practiceResultsState.classList.add('opacity-0', 'scale-95');
        setTimeout(() => {
            practiceResultsState.classList.add('hidden');
            practiceInputState.classList.remove('hidden');
            pracMicBtn.classList.add('bg-indigo-600');
            pracBtnBg.classList.remove('opacity-100'); pracBtnBg.classList.add('opacity-0');
            pracMicIcon.classList.add('bg-indigo-800/50'); pracMicIcon.classList.remove('bg-white/30', 'scale-105');
            pracMicText.textContent = "Read Aloud"; pracMicSubtext.textContent = "Tap when ready";
            pracVoiceBars.classList.add('opacity-0', 'scale-95'); pracVoiceBars.classList.remove('animate-voice', 'scale-100');
            setTimeout(() => {
                practiceInputState.classList.remove('opacity-0', '-translate-y-5', 'scale-95');
            }, 50);
        }, 300);
    }

    pracMicBtn.addEventListener('click', handlePracMicClick);
    pracResetBtn.addEventListener('click', resetPractice);

    updateConvLanguageUI();
});