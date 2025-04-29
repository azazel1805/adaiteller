document.addEventListener('DOMContentLoaded', () => {
    // --- DOM Elements (IDs match the HTML provided) ---
    const storyForm = document.getElementById('story-form');
    const startButton = document.getElementById('start-button'); // ID from your HTML button
    const charactersInput = document.getElementById('characters'); // ID from your HTML textarea
    const settingInput = document.getElementById('setting'); // ID from your HTML textarea
    const otherDetailsInput = document.getElementById('other-details'); // ID from your HTML textarea
    const genreSelect = document.getElementById('genre-select'); // ID from your HTML select
    const lengthSelect = document.getElementById('length-select'); // ID from your HTML select
    const languageSelect = document.getElementById('language-select'); // ID from your HTML select

    const storyDisplaySection = document.getElementById('story-display-section');
    const storyOutput = document.getElementById('story-output');
    const controlsDiv = document.getElementById('controls');
    const nextInstructionsInput = document.getElementById('next-instructions'); // ID from your HTML input
    const continueButton = document.getElementById('continue-button'); // ID from your HTML button
    const endButton = document.getElementById('end-button'); // ID from your HTML button
    const resetButton = document.getElementById('reset-button'); // ID from your HTML button

    const loadingIndicator = document.getElementById('loading');
    const errorMessageDiv = document.getElementById('error-message');

    // --- State ---
    let storyHistory = []; // Array to hold generated story parts (strings)
    let currentInputs = {}; // Object to hold the initial story settings
    let isGenerating = false; // Flag to prevent concurrent requests

    // --- Functions ---

    function showLoading() {
        isGenerating = true;
        loadingIndicator.style.display = 'flex';
        errorMessageDiv.style.display = 'none'; // Hide errors when loading starts
        // Disable all action buttons during generation
        startButton.disabled = true;
        continueButton.disabled = true;
        endButton.disabled = true;
        resetButton.disabled = true; // Also disable reset while generating
    }

    function hideLoading() {
        isGenerating = false;
        loadingIndicator.style.display = 'none';
        // Re-enable buttons based on current story state
        startButton.disabled = storyHistory.length > 0; // Keep start disabled if story started
        continueButton.disabled = storyHistory.length === 0; // Enable continue if history exists
        endButton.disabled = storyHistory.length === 0; // Enable end if history exists
        resetButton.disabled = false; // Always enable reset when not loading
    }

    function displayError(message) {
        // Sanitize message slightly (optional, backend should ideally send safe strings)
        const safeMessage = String(message).replace(/</g, "<").replace(/>/g, ">");
        errorMessageDiv.innerHTML = `⚠️ Error: ${safeMessage}`; // Use innerHTML potentially if backend sends formatted errors, but be cautious. textContent is safer.
        //errorMessageDiv.textContent = `⚠️ Error: ${message}`; // Safer option
        errorMessageDiv.style.display = 'block';
        hideLoading(); // Ensure loading is hidden and buttons re-enabled on error
    }

    function updateStoryDisplay() {
        storyOutput.innerHTML = ''; // Clear previous content
        if (storyHistory.length === 0) {
            storyOutput.textContent = 'Your generated story will appear here...'; // Placeholder
            return;
        }

        storyHistory.forEach((part, index) => {
            const partDiv = document.createElement('div');
            partDiv.classList.add('story-part');

            const title = document.createElement('h3');
            title.textContent = `Part ${index + 1}`;
            partDiv.appendChild(title);

            // Create a paragraph for the content to allow CSS styling like white-space: pre-wrap
            const contentP = document.createElement('p');
            contentP.textContent = part; // Use textContent for security
            partDiv.appendChild(contentP);

            storyOutput.appendChild(partDiv);
        });

        // Scroll the container of the parts to the bottom
         storyDisplaySection.scrollIntoView({ behavior: 'smooth', block: 'end' }); // Scroll section into view
         // Alternatively, scroll the output div itself if it has its own scrollbar:
         // storyOutput.scrollTop = storyOutput.scrollHeight;
    }

    async function generatePart(action, instructions = null) {
        if (isGenerating) {
            console.warn("Generation already in progress.");
            return; // Prevent multiple simultaneous requests
        }

        showLoading();
        errorMessageDiv.style.display = 'none'; // Clear previous errors

        // Prepare payload - keys MUST match what app.py expects in request.get_json()
        const payload = {
            action: action,
            inputs: currentInputs, // Contains characters, setting, genre, length, language, other_details
            history: storyHistory, // Array of strings
            instructions: action === 'continue' ? instructions : null // String or null
        };

        console.log("Sending payload:", payload); // Debug: Log payload

        try {
            const response = await fetch('/generate', { // Ensure this endpoint matches Flask route
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json' // Explicitly accept JSON
                },
                body: JSON.stringify(payload),
            });

            // Always try to parse JSON, even for errors, as backend sends error details in JSON
            const data = await response.json();

            if (!response.ok) {
                // Handle HTTP errors (4xx, 5xx) - Use error message from backend JSON if available
                console.error("Server returned error:", response.status, data);
                throw new Error(data.error || `Request failed with status: ${response.status}`);
            }

            // Handle logical errors returned in JSON payload (even with 200 OK status)
            if (data.error) {
                 console.error("Backend returned logical error:", data.error);
                 displayError(data.error);
            } else if (data.story_part) {
                 // Success!
                 storyHistory.push(data.story_part);
                 updateStoryDisplay(); // Update UI with the new part

                 // Ensure story section and controls are visible
                 storyDisplaySection.style.display = 'block';
                 controlsDiv.style.display = 'flex'; // Show continue/end controls
                 resetButton.style.display = 'block'; // Show reset button (might want 'inline-block' or adjust CSS)

                 nextInstructionsInput.value = ''; // Clear instructions input after successful use

                 if (action === 'end') {
                     controlsDiv.style.display = 'none'; // Hide continue/end controls after finishing
                     console.log('Story finished!');
                     // Maybe display a "Story Complete" message?
                 }
                 hideLoading(); // Hide loading indicator on success
            } else {
                // Unexpected case: Response OK but no story_part and no error message
                 console.error("Unexpected response:", data);
                 displayError("Received an empty or unexpected response from the server.");
            }

        } catch (error) {
            console.error('Generation Fetch/Processing Error:', error);
            hideLoading(); // Ensure loading is hidden on any error
            // Display a user-friendly message, potentially different for network vs. other errors
            if (error.message.includes("Failed to fetch")) {
                displayError("Network error. Unable to connect to the server. Please check your connection.");
            } else {
                 displayError(error.message || 'An unknown error occurred. Check the console for details.');
            }
        }
    }


    // --- Event Listeners ---

    // Use the correct button ID ('start-button') for starting
    startButton.addEventListener('click', () => {
        // Use 'button' type click, not form 'submit'

        // Collect inputs - use the correct IDs from HTML elements
        // Keys here MUST match what `build_prompt` expects in `inputs` object
        currentInputs = {
            characters: charactersInput.value.trim(),
            setting: settingInput.value.trim(),
            // Use 'other_details' key as expected by backend
            other_details: otherDetailsInput.value.trim(),
            genre: genreSelect.value,
            length: lengthSelect.value, // This sends 'short', 'medium', etc.
            language: languageSelect.value
        };

        // Basic frontend validation
        if (!currentInputs.characters || !currentInputs.setting || !currentInputs.genre) {
            displayError("Please fill in Characters, Setting, and select a Genre.");
            // Highlight missing fields? (Optional enhancement)
            return;
        }
         if (!currentInputs.length) { // Should always have a value due to 'selected', but good check
             displayError("Please select a story part length.");
             return;
         }
         if (!currentInputs.language) {
             displayError("Please select a language.");
             return;
         }


        storyHistory = []; // Reset history for a new story
        storyOutput.innerHTML = ''; // Clear display
        errorMessageDiv.style.display = 'none'; // Clear previous errors
        storyDisplaySection.style.display = 'none'; // Hide until first part arrives
        controlsDiv.style.display = 'none';
        resetButton.style.display = 'none';

        // Disable the start button immediately after clicking
        startButton.disabled = true;

        generatePart('start'); // Call the generation function
    });

    // Use correct ID for continue button
    continueButton.addEventListener('click', () => {
        const instructions = nextInstructionsInput.value.trim(); // Get instructions
        generatePart('continue', instructions || null); // Pass instructions or null if empty
    });

    // Use correct ID for end button
    endButton.addEventListener('click', () => {
        // Optionally confirm ending the story?
        generatePart('end');
    });

    // Use correct ID for reset button
    resetButton.addEventListener('click', () => {
        // Optional: Confirmation dialog?
        // if (!confirm("Are you sure you want to start a new story? The current one will be lost.")) {
        //     return;
        // }

        storyHistory = [];
        currentInputs = {}; // Clear stored inputs
        storyOutput.innerHTML = 'Your generated story will appear here...'; // Reset placeholder
        errorMessageDiv.style.display = 'none'; // Hide errors
        storyDisplaySection.style.display = 'none'; // Hide story area
        controlsDiv.style.display = 'none'; // Hide controls
        resetButton.style.display = 'none'; // Hide reset button itself
        storyForm.reset(); // Reset form fields to defaults

        // Re-enable start button, disable others
        startButton.disabled = false;
        continueButton.disabled = true;
        endButton.disabled = true;
        isGenerating = false; // Ensure state is reset

        console.log('Story reset.');
        // Scroll back to top?
        window.scrollTo({ top: 0, behavior: 'smooth' });
    });

    // Initial setup on load
    updateStoryDisplay(); // Show initial placeholder in story output
    startButton.disabled = false; // Ensure start is enabled initially
    continueButton.disabled = true; // Start disabled
    endButton.disabled = true; // Start disabled


}); // End DOMContentLoaded
