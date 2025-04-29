import google.generativeai as genai
import os
import json # Although Flask handles JSON well, sometimes useful
from dotenv import load_dotenv
from flask import Flask, request, jsonify, render_template, abort

# --- Configuration ---
MODEL_NAME = "gemini-1.5-flash" # Or your preferred model

# Define choices internally (mapping from values sent by JS)
# These need to match the 'value' attributes in the HTML select options
LENGTH_CHOICES_MAP = {
    "short": (250, 500),
    "medium": (500, 1000),
    "long": (1000, 1500),
    "epic": (1500, 2000),
}
# Language and Genre are passed directly as strings

# --- Helper Functions ---

def load_api_key():
    """Loads the Gemini API key from the .env file."""
    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("Error: GEMINI_API_KEY not found in .env file.")
        print("Please create a '.env' file in the root directory with:")
        print("GEMINI_API_KEY=YOUR_API_KEY_HERE")
        # In a real app, you might raise an exception or handle this more gracefully
    return api_key

def configure_gemini(api_key):
    """Configures the Generative AI client."""
    if not api_key:
        return None
    try:
        genai.configure(api_key=api_key)
        # Add generation config if needed (temperature, top_p, etc.)
        # generation_config = genai.types.GenerationConfig(temperature=0.7)
        model = genai.GenerativeModel(
            MODEL_NAME,
            # generation_config=generation_config
            )
        return model
    except Exception as e:
        print(f"Error configuring Gemini: {e}")
        return None

def build_prompt(inputs, story_history, action="start", next_part_instructions=None):
    """Builds the prompt for the Gemini API."""
    length_key = inputs.get('length', 'medium') # Default to medium if not provided
    min_words, max_words = LENGTH_CHOICES_MAP.get(length_key, LENGTH_CHOICES_MAP['medium'])
    language = inputs.get('language', 'English')
    genre = inputs.get('genre', 'Adventure') # Default genre

    prompt = f"You are a creative storyteller writing a story in {language}."
    prompt += f" The story genre is {genre}.\n"
    prompt += f"Main characters: {inputs.get('characters', 'A brave adventurer')}\n"
    prompt += f"Setting: {inputs.get('setting', 'A mysterious forest')}\n"
    if inputs.get('other_details'):
        prompt += f"Initial details: {inputs.get('other_details')}\n"

    # Add context from history if continuing or ending
    if action in ["continue", "end"] and story_history:
        prompt += "\nHere is the story so far (most recent parts first for context):\n---\n"
        # Limit context to avoid exceeding token limits
        context_limit = 2 # Number of previous parts to include
        context = "\n\n...\n\n".join(story_history[-context_limit:])
        prompt += context
        prompt += "\n---\n"

    # Add action instruction
    if action == "start":
        prompt += f"\nWrite the *first part* of the story. It should be approximately {min_words}-{max_words} words long. Establish the scene and introduce the character(s)."
    elif action == "continue":
        prompt += f"\nWrite the *next part* of the story, continuing logically from where the previous part ended. Maintain the established tone and characters."
        if next_part_instructions:
             prompt += f" Specific focus for this part: {next_part_instructions}."
        prompt += f" This part should be approximately {min_words}-{max_words} words long and written in {language}."
    elif action == "end":
        prompt += "\nHere is the story so far:\n---\n"
        # Include more history for the end if possible within limits
        full_context = "\n\n...\n\n".join(story_history)
        prompt += full_context # Potentially long, model should handle truncation if needed
        prompt += "\n---\n"
        prompt += f"\nWrite the *concluding part* of the story. Bring the current plot points to a satisfying resolution based on the genre and events so far."
        prompt += f" The conclusion should be approximately {min_words}-{max_words} words long and written in {language}."

    # print(f"DEBUG: Prompt for {action}:\n{prompt[:500]}...") # Debugging prompt
    return prompt

# --- Flask App ---
app = Flask(__name__)
api_key = load_api_key()
model = configure_gemini(api_key)

@app.route('/')
def index():
    """Serves the main HTML page."""
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate():
    """Handles story generation requests from the frontend."""
    if not model:
        return jsonify({'error': 'Story generation model not configured. Check API Key.'}), 500
    if not request.is_json:
        return jsonify({'error': 'Request must be JSON'}), 400

    data = request.get_json()
    action = data.get('action')
    inputs = data.get('inputs')
    history = data.get('history', []) # Get previous story parts
    instructions = data.get('instructions') # For 'continue' action

    if not action or not inputs:
        return jsonify({'error': 'Missing action or inputs in request'}), 400

    # Basic input validation (can be more robust)
    if action not in ['start', 'continue', 'end']:
        return jsonify({'error': 'Invalid action specified'}), 400
    if action == 'start' and not all(k in inputs for k in ['characters', 'setting', 'genre', 'length', 'language']):
         return jsonify({'error': 'Missing required input fields for starting story'}), 400
    if action in ['continue', 'end'] and not history:
         # Allow continuing/ending without history just in case, but maybe warn
         pass # Or return jsonify({'error': 'Cannot continue/end without story history'}), 400


    try:
        prompt = build_prompt(inputs, history, action, instructions)
        print(f"Attempting generation for action: {action}") # Server log
        # Safety settings can be adjusted if needed
        # safety_settings = [...]
        response = model.generate_content(
            prompt,
            # safety_settings=safety_settings
            )

        # --- Handle Response ---
        # Check for safety blocks or empty response more robustly
        generated_text = None
        error_message = None

        if response.prompt_feedback.block_reason:
            error_message = f"Generation blocked due to: {response.prompt_feedback.block_reason}"
            print(f"Generation Blocked: {error_message}") # Server log
            if response.candidates:
                 print(f"Candidate Safety Ratings: {response.candidates[0].safety_ratings}")

        elif not response.parts:
             # Sometimes no parts but also no block reason? Check candidates.
             if response.candidates and response.candidates[0].content.parts:
                 generated_text = response.candidates[0].content.text # Use text from candidate
             elif response.candidates and response.candidates[0].finish_reason != "STOP":
                  error_message = f"Generation stopped unexpectedly. Reason: {response.candidates[0].finish_reason}"
                  print(f"Generation Failed: {error_message}") # Server log
                  if response.candidates[0].safety_ratings:
                       print(f"Candidate Safety Ratings: {response.candidates[0].safety_ratings}")
             else:
                 error_message = "Generation failed: Received an empty response from the API."
                 print(error_message) # Server log

        else:
            generated_text = response.text # Get the text if parts exist

        # --- Return Result ---
        if generated_text:
            print(f"Generation Successful. Part length: {len(generated_text)} chars.") # Server log
            return jsonify({'story_part': generated_text})
        else:
            # Ensure an error message is set if text is None
            if not error_message:
                 error_message = "An unknown generation error occurred."
            return jsonify({'error': error_message}), 500 # Internal server error type

    except Exception as e:
        print(f"Error during generation: {e}") # Log the full error
        # Provide a generic error to the client
        return jsonify({'error': f'An internal server error occurred during generation: {type(e).__name__}'}), 500


if __name__ == '__main__':
    # Use debug=True for development only, it auto-reloads
    app.run(debug=True, port=5001) # Use a different port if 5000 is busy