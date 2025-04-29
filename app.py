import google.generativeai as genai
import os
import json
from dotenv import load_dotenv
from flask import Flask, request, jsonify, render_template, abort

# --- Configuration ---
MODEL_NAME = "gemini-1.5-flash" # Or your preferred model

# Define choices internally (mapping from values sent by JS)
# These need to match the 'value' attributes in the HTML select options
# Using lowercase keys as they come from the <select> value attributes
LENGTH_CHOICES_MAP = {
    "short": (250, 500),    # Corresponds to value="short" in HTML
    "medium": (500, 1000),   # Corresponds to value="medium"
    "long": (1000, 1500),    # Corresponds to value="long"
    "epic": (1500, 2000),    # Corresponds to value="epic"
}
# Language and Genre are passed directly as strings

# --- Helper Functions ---

def load_api_key():
    """Loads the Gemini API key from environment variables or .env file."""
    load_dotenv() # Load .env file if it exists (useful for local dev)
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("Warning: GEMINI_API_KEY not found in environment variables or .env file.")
        print("Ensure it is set as a Secret Environment Variable on Render.")
    return api_key

def configure_gemini(api_key):
    """Configures the Generative AI client."""
    if not api_key:
        print("Gemini API key not available. Story generation will fail.")
        return None # Return None if no key
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(MODEL_NAME)
        print("Gemini model configured successfully.")
        return model
    except Exception as e:
        print(f"Error configuring Gemini: {e}")
        return None

def build_prompt(inputs, story_history, action="start", next_part_instructions=None):
    """Builds the prompt for the Gemini API."""
    # Get inputs using the keys expected from the frontend JS payload
    length_key = inputs.get('length', 'medium') # Default if missing
    min_words, max_words = LENGTH_CHOICES_MAP.get(length_key, LENGTH_CHOICES_MAP['medium'])

    language = inputs.get('language', 'English')
    genre = inputs.get('genre', 'Adventure')
    characters = inputs.get('characters', 'A mysterious traveler')
    setting = inputs.get('setting', 'A place lost to time')
    other_details = inputs.get('other_details', None) # Can be None/empty

    prompt = f"You are a creative storyteller writing a story in {language}."
    prompt += f" The story genre is {genre}.\n"
    prompt += f"Main characters: {characters}\n"
    prompt += f"Setting: {setting}\n"
    if other_details: # Only add if provided
        prompt += f"Initial details: {other_details}\n"

    # Add context from history
    if action in ["continue", "end"] and story_history:
        prompt += "\nHere is the story so far (most recent parts first for context):\n---\n"
        context_limit = 2 # Include last 2 parts for context (adjust as needed)
        context = "\n\n...\n\n".join(story_history[-context_limit:])
        prompt += context
        prompt += "\n---\n"

    # Add action instruction
    if action == "start":
        prompt += f"\nWrite the *first part* of the story. It should be approximately {min_words}-{max_words} words long. Establish the scene and introduce the character(s) based on the provided details."
    elif action == "continue":
        prompt += f"\nWrite the *next part* of the story, continuing logically from where the previous part ended. Maintain the established tone, characters, and {genre} genre."
        if next_part_instructions:
             prompt += f" Specific focus or direction for this part: {next_part_instructions}."
        prompt += f" This part should be approximately {min_words}-{max_words} words long and written in {language}."
    elif action == "end":
        # Use full history for ending prompt if possible, let model handle context length
        prompt += "\nHere is the full story generated so far:\n---\n"
        full_context = "\n\n".join(story_history) # Join with double newline for readability
        prompt += full_context
        prompt += "\n---\n"
        prompt += f"\nWrite the *concluding part* of the story. Bring the current plot points to a satisfying resolution based on the {genre} genre and events so far."
        prompt += f" The conclusion should be approximately {min_words}-{max_words} words long and written in {language}."

    # print(f"DEBUG: Prompt for {action}:\n{prompt[:500]}...") # Uncomment for debugging
    return prompt

# --- Flask App ---
app = Flask(__name__) # Looks for templates in 'templates', static in 'static'

api_key = load_api_key()
model = configure_gemini(api_key) # Configure on startup

@app.route('/')
def index():
    """Serves the main HTML page."""
    return render_template('index.html')

# Optional: Explicitly serve PWA files if needed (Flask static usually handles this)
# Test without these first. Add them if you have issues with caching or routing.
# from flask import send_from_directory
# @app.route('/manifest.json')
# def serve_manifest():
#     return send_from_directory('static', 'manifest.json', mimetype='application/manifest+json')
#
# @app.route('/sw.js')
# def serve_sw():
#     # Set cache control headers for the service worker file itself
#     response = send_from_directory('static', 'sw.js', mimetype='application/javascript')
#     response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
#     response.headers['Pragma'] = 'no-cache'
#     response.headers['Expires'] = '0'
#     return response


@app.route('/generate', methods=['POST'])
def generate():
    """Handles story generation requests from the frontend."""
    if not model:
        return jsonify({'error': 'Story generation model not configured. Check API Key environment variable.'}), 500
    if not request.is_json:
        return jsonify({'error': 'Request must be JSON'}), 400

    data = request.get_json()
    action = data.get('action')
    inputs = data.get('inputs') # This should contain keys like 'characters', 'setting', 'genre', 'length', 'language', 'other_details'
    history = data.get('history', []) # List of previous story parts (strings)
    instructions = data.get('instructions') # String for 'continue' action

    # --- Input Validation ---
    if not action or not inputs:
        return jsonify({'error': 'Missing action or inputs in request'}), 400
    if action not in ['start', 'continue', 'end']:
        return jsonify({'error': 'Invalid action specified'}), 400
    # Check required inputs for starting a story
    if action == 'start':
         required_start_keys = ['characters', 'setting', 'genre', 'length', 'language']
         if not all(k in inputs and inputs[k] for k in required_start_keys):
             # Check if specific key is missing or empty
             missing = [k for k in required_start_keys if k not in inputs or not inputs[k]]
             return jsonify({'error': f'Missing required input field(s) for starting story: {", ".join(missing)}'}), 400
    # History is required for continue/end, but allow flexibility if frontend sends empty
    # if action in ['continue', 'end'] and not history:
    #      print("Warning: Received continue/end action without history.")
    #      # return jsonify({'error': 'Cannot continue or end without story history'}), 400 # Stricter

    try:
        prompt = build_prompt(inputs, history, action, instructions)
        print(f"Attempting generation for action: {action} with length key: {inputs.get('length')}") # Server log

        # Safety settings (optional, adjust as needed)
        # safety_settings = {
        #     'HARM_CATEGORY_HARASSMENT': 'BLOCK_MEDIUM_AND_ABOVE',
        #     'HARM_CATEGORY_HATE_SPEECH': 'BLOCK_MEDIUM_AND_ABOVE',
        #     'HARM_CATEGORY_SEXUALLY_EXPLICIT': 'BLOCK_MEDIUM_AND_ABOVE',
        #     'HARM_CATEGORY_DANGEROUS_CONTENT': 'BLOCK_MEDIUM_AND_ABOVE',
        # }

        response = model.generate_content(
            prompt,
            # safety_settings=safety_settings
            )

        # --- Handle Response ---
        generated_text = None
        error_message = None

        try:
            # Accessing response parts safely
            if response.parts:
                 generated_text = response.text # Preferred way if parts exist
            # Check for blocking even if parts seems empty
            elif response.prompt_feedback and response.prompt_feedback.block_reason:
                 error_message = f"Generation blocked due to: {response.prompt_feedback.block_reason}"
                 print(f"Generation Blocked: {error_message}")
                 # Log safety ratings if available (might be in candidates)
                 if response.candidates and hasattr(response.candidates[0], 'safety_ratings'):
                     print(f"Candidate Safety Ratings: {response.candidates[0].safety_ratings}")
            # Check finish reason if no text and no explicit block reason
            elif response.candidates and response.candidates[0].finish_reason != "STOP":
                finish_reason = response.candidates[0].finish_reason
                error_message = f"Generation stopped unexpectedly. Reason: {finish_reason}"
                print(f"Generation Failed: {error_message}")
                if hasattr(response.candidates[0], 'safety_ratings'):
                    print(f"Candidate Safety Ratings: {response.candidates[0].safety_ratings}")
            else:
                 # Catch-all for empty response without clear reason
                 error_message = "Generation failed: Received an empty or unexpected response from the API."
                 print(error_message)
                 print(f"Raw Response Info: Prompt Feedback={response.prompt_feedback}, Candidates={response.candidates}")


        except ValueError as ve: # Handles potential issues with response.text if content is blocked
             error_message = f"Error accessing generated text. Generation might be blocked. Details: {ve}"
             print(error_message)
             if response.prompt_feedback and response.prompt_feedback.block_reason:
                 print(f"Block Reason: {response.prompt_feedback.block_reason}")

        except AttributeError as ae:
             error_message = "Generation failed: Unexpected response structure from API."
             print(f"{error_message} Details: {ae}")
             print("Response object:", response) # Log the raw response if possible
        except Exception as resp_err: # Catch other potential response processing errors
             error_message = f"Generation failed: Error processing API response ({type(resp_err).__name__})."
             print(f"{error_message} Details: {resp_err}")


        # --- Return Result ---
        if generated_text:
            print(f"Generation Successful. Part length: {len(generated_text)} chars.") # Server log
            return jsonify({'story_part': generated_text})
        else:
            # Ensure an error message is set if text is None/empty
            if not error_message:
                 error_message = "An unknown generation error occurred (empty response)."
                 print(error_message) # Log if it hits this state
            return jsonify({'error': error_message}), 500 # Use 500 for server-side/API issues

    except Exception as e:
        print(f"Critical Error during generation request processing: {e}") # Log the full error
        import traceback
        print(traceback.format_exc()) # Print stack trace for debugging
        # Provide a generic error to the client
        return jsonify({'error': f'An internal server error occurred: {type(e).__name__}'}), 500

# Gunicorn will run the app, so the following is not needed for Render deployment.
# It's useful for running locally directly with `python app.py`.
# if __name__ == '__main__':
#     print("Attempting to run locally...")
#     # Ensure API key is loaded for local run if not set globally
#     api_key_local = load_api_key()
#     if not api_key_local:
#          print("FATAL: API Key not found. Cannot run locally.")
#     else:
#          model = configure_gemini(api_key_local) # Reconfigure if needed
#          if model:
#              # Use a different port like 5001 if 5000 is common
#              app.run(debug=True, host='0.0.0.0', port=5001)
#          else:
#              print("FATAL: Model could not be configured. Cannot run locally.")
