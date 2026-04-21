/**
 * Web Speech API wrapper for BreedSense AI Voice Output
 */

function speakPrediction(breedName) {
    // Check if the browser supports speech synthesis
    if ('speechSynthesis' in window) {
        // Cancel any currently playing speech to avoid overlapping
        window.speechSynthesis.cancel();
        
        // Define the speech utterance
        const textToAnnounce = `This is a ${breedName}.`;
        const utterance = new SpeechSynthesisUtterance(textToAnnounce);
        
        // Tweak settings for a natural voice
        utterance.pitch = 1.0; // Normal pitch
        utterance.rate = 0.95;  // Slightly slower than default for clarity
        utterance.volume = 1.0; // Max volume
        
        // Attempt to find a suitable English voice (preferably a natural-sounding one)
        const voices = window.speechSynthesis.getVoices();
        if (voices.length > 0) {
            // Try to find a premium/Google voice, fallback to first English voice
            const preferredVoice = voices.find(v => v.name.includes('Google US English') || v.name.includes('Natural')) 
                                || voices.find(v => v.lang.startsWith('en-'));
            if (preferredVoice) {
                utterance.voice = preferredVoice;
            }
        }
        
        // Fire the speech API
        window.speechSynthesis.speak(utterance);
    } else {
        console.warn('Speech Synthesis API is not supported in this browser.');
    }
}

// Pre-load voices to ensure they are available when the function is called
if ('speechSynthesis' in window) {
    window.speechSynthesis.onvoiceschanged = () => {
        window.speechSynthesis.getVoices();
    };
}
