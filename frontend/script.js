document.addEventListener('DOMContentLoaded', () => {

    // ================= BUTTON / VIEW SETUP =================
    const navConvBtn = document.getElementById('nav-conv-btn');
    const navPracBtn = document.getElementById('nav-prac-btn');
    const conversationView = document.getElementById('conversation-view');
    const practiceView = document.getElementById('practice-view');

    function switchToConversation() {
        conversationView.classList.add('active-view');
        conversationView.classList.remove('hidden-view');

        practiceView.classList.remove('active-view');
        practiceView.classList.add('hidden-view');
    }

    function switchToPractice() {
        practiceView.classList.add('active-view');
        practiceView.classList.remove('hidden-view');

        conversationView.classList.remove('active-view');
        conversationView.classList.add('hidden-view');
    }

    navConvBtn.addEventListener('click', switchToConversation);
    navPracBtn.addEventListener('click', switchToPractice);


    // ================= CONVERSATION MODE MIC LOGIC =================
    const convMicBtn = document.getElementById('conv-mic-btn');
    const convMicIcon = document.getElementById('conv-mic-icon');
    const convMicText = document.getElementById('conv-mic-text');
    const convMicSubtext = document.getElementById('conv-mic-subtext');
    const convVoiceBars = document.getElementById('conv-voice-bars');

    let convMediaRecorder = null;
    let convAudioChunks = [];
    let convStream = null;
    let isConvMicActive = false;

    // ========== Backend Upload Function ==========
    async function uploadAudioToBackend(audioBlob) {
        console.log("Uploading blob:", audioBlob);

        try {
            const formData = new FormData();
            formData.append("file", audioBlob, "audio.webm");

            const response = await fetch("http://localhost:8000/api/reply", {
                method: "POST",
                body: formData
            });

            const result = await response.json();
            console.log("Server responded:", result);

        } catch (err) {
            console.error("Upload failed:", err);
        }
    }


    // ========== MIC TOGGLE ==========
    async function handleConvMicToggle() {
        console.log("Mic clicked");

        isConvMicActive = !isConvMicActive;

        if (isConvMicActive) {
            console.log("Starting recording...");

            try {
                convStream = await navigator.mediaDevices.getUserMedia({ audio: true });

                convAudioChunks = [];
                convMediaRecorder = new MediaRecorder(convStream, {
                    mimeType: "audio/webm"
                });

                convMediaRecorder.ondataavailable = e => convAudioChunks.push(e.data);

                convMediaRecorder.start();

                // UI updates
                convMicBtn.classList.add('active-state');
                convMicIcon.classList.remove('ph-microphone');
                convMicIcon.classList.add('ph-waveform', 'animate-pulse');
                convMicText.textContent = "Listening...";
                convMicSubtext.textContent = "Speak clearly";
                convVoiceBars.classList.add('animate-voice');

            } catch (err) {
                console.error("MIC ERROR:", err);
                alert("Microphone blocked. Check browser permissions.");
                isConvMicActive = false;
            }

        } else {
            console.log("Stopping recording...");

            convMediaRecorder.stop();

            convMediaRecorder.onstop = async () => {
                console.log("Recorder stopped");

                const audioBlob = new Blob(convAudioChunks, { type: "audio/webm" });

                // Stop audio stream
                convStream.getTracks().forEach(t => t.stop());

                console.log("Final blob:", audioBlob);
                uploadAudioToBackend(audioBlob);
            };

            // UI back to normal
            convMicBtn.classList.remove('active-state');
            convMicIcon.classList.remove('ph-waveform', 'animate-pulse');
            convMicIcon.classList.add('ph-microphone');
            convMicText.textContent = "Tap to speak";
            convMicSubtext.textContent = "VISUAL DEMO ONLY";
            convVoiceBars.classList.remove('animate-voice');
        }
    }

    convMicBtn.addEventListener('click', handleConvMicToggle);

    console.log("Mic script ready. Click the button to test.");
});
