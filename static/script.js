document.addEventListener('DOMContentLoaded', () => {
    // --- DOM Elements ---
    const storyForm = document.getElementById('story-form');
    const startButton = document.getElementById('start-button');
    const charactersInput = document.getElementById('characters');
    const settingInput = document.getElementById('setting');
    const otherDetailsInput = document.getElementById('other-details');
    const genreSelect = document.getElementById('genre-select');
    const lengthSelect = document.getElementById('length-select');
    const languageSelect = document.getElementById('language-select');

    const storyDisplaySection = document.getElementById('story-display-section');
    const storyOutput = document.getElementById('story-output');
    const controlsDiv = document.getElementById('controls');
    const nextInstructionsInput = document.getElementById('next-instructions');
    const continueButton = document.getElementById('continue-button');
    const endButton = document.getElementById('end-button');
    const resetButton = document.getElementById('reset-button');

    const loadingIndicator = document.getElementById('loading');
    const errorMessageDiv = document.getElementById('error-message');

    // --- State ---
    let storyHistory = [];
    let currentInputs = {};
    let isGenerating = false;

    // --- Functions ---

    function showLoading() {
        isGenerating = true;
        loadingIndicator.style.display = 'flex';
        errorMessageDiv.style.display = 'none'; // Hide errors when loading starts
        startButton.disabled = true;
        continueButton.disabled = true;
        endButton.disabled = true;
    }

    function hideLoading() {
        isGenerating = false;
        loadingIndicator.style.display = 'none';
        // Re-enable buttons based on state (don't enable start if story began)
        startButton.disabled = storyHistory.length > 0;
        continueButton.disabled = false;
        endButton.disabled = false;
    }

    function displayError(message) {
        errorMessageDiv.textContent = `Error: ${message}`;
        errorMessageDiv.style.display = 'block';
        hideLoading(); // Ensure loading is hidden if error occurs
    }

    function updateStoryDisplay() {
        storyOutput.innerHTML = ''; // Clear previous content
        storyHistory.forEach((part, index) => {
            const partDiv = document.createElement('div');
            partDiv.classList.add('story-part');

            const title = document.createElement('h3');
            title.textContent = `Part ${index + 1}`;
            partDiv.appendChild(title);

            const content = document.createElement('p');
            // Use textContent to prevent potential XSS if the AI somehow includes HTML
            content.textContent = part;
            partDiv.appendChild(content);

            storyOutput.appendChild(partDiv);
        });

        // Scroll to the bottom of the story output
        storyOutput.scrollTop = storyOutput.scrollHeight;
    }

    async function generatePart(action, instructions = null) {
        if (isGenerating) return; // Prevent multiple simultaneous requests

        showLoading();

        const payload = {
            action: action,
            inputs: currentInputs,
            history: storyHistory,
            instructions: action === 'continue' ? instructions : null
        };

        try {
            const response = await fetch('/generate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(payload),
            });

            const data = await response.json();
            hideLoading(); // Hide loading before processing result

            if (!response.ok) {
                // Handle HTTP errors (4xx, 5xx) with error message from backend JSON
                throw new Error(data.error || `HTTP error! Status: ${response.status}`);
            }

            if (data.error) {
                // Handle logical errors returned in JSON payload even with 200 OK (though backend should use 500)
                 displayError(data.error);
            } else if (data.story_part) {
                 storyHistory.push(data.story_part);
                 updateStoryDisplay();
                 storyDisplaySection.style.display = 'block'; // Show story section
                 controlsDiv.style.display = 'flex';        // Show continue/end controls
                 resetButton.style.display = 'block';       // Show reset button
                 nextInstructionsInput.value = ''; // Clear instructions after use

                if (action === 'end') {
                     controlsDiv.style.display = 'none'; // Hide controls after finishing
                     console.log('Story finished!');
                 }
            } else {
                // Unexpected: No error and no story_part
                 displayError("Received an unexpected response from the server.");
            }

        } catch (error) {
            console.error('Generation Fetch Error:', error);
            hideLoading();
            displayError(error.message || 'Failed to communicate with the server. Check console.');
        }
    }


    // --- Event Listeners ---

    storyForm.addEventListener('submit', (event) => {
        event.preventDefault(); // Prevent default page reload

        // Collect inputs
        currentInputs = {
            characters: charactersInput.value.trim(),
            setting: settingInput.value.trim(),
            other_details: otherDetailsInput.value.trim(),
            genre: genreSelect.value,
            length: lengthSelect.value,
            language: languageSelect.value
        };

        // Basic frontend validation (optional, as backend validates too)
        if (!currentInputs.characters || !currentInputs.setting || !currentInputs.genre) {
            displayError("Please fill in Characters, Setting, and select a Genre.");
            return;
        }

        storyHistory = []; // Reset history for a new story
        storyOutput.innerHTML = ''; // Clear display
        storyDisplaySection.style.display = 'none'; // Hide until first part arrives
        controlsDiv.style.display = 'none';
        resetButton.style.display = 'none';

        generatePart('start');
    });

    continueButton.addEventListener('click', () => {
        const instructions = nextInstructionsInput.value.trim();
        generatePart('continue', instructions);
    });

    endButton.addEventListener('click', () => {
        generatePart('end');
    });

    resetButton.addEventListener('click', () => {
        storyHistory = [];
        currentInputs = {};
        storyOutput.innerHTML = '';
        storyDisplaySection.style.display = 'none';
        controlsDiv.style.display = 'none';
        resetButton.style.display = 'none';
        errorMessageDiv.style.display = 'none';
        storyForm.reset(); // Reset form fields
        startButton.disabled = false; // Re-enable start button
        isGenerating = false; // Ensure state is reset
        console.log('Story reset.');
    });

}); // End DOMContentLoaded