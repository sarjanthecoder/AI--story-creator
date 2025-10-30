import os
import google.generativeai as genai
from flask import Flask, request, jsonify, render_template

app = Flask(__name__)

# --- API Key Configuration ---
try:
    # Best practice: Use an environment variable for the API key.
    genai.configure(api_key=os.environ["GEMINI_API_KEY"])
except KeyError:
    print("WARNING: GEMINI_API_KEY environment variable not set.")
    # For quick testing, you can add your key here (NOT recommended for production)
    # genai.configure(api_key="YOUR_API_KEY_HERE")

# --- Page Routes ---

@app.route('/')
def landing_page():
    """Renders the landing page."""
    # Assuming your HTML file is named 'index.html'
    return render_template('index.html')

# --- API Route for Story Generation ---

@app.route('/generate_story', methods=['POST'])
def generate_story():
    """API endpoint to generate a story based on detailed user inputs."""
    try:
        data = request.get_json()
        if not data or 'prompt' not in data:
            return jsonify({"error": "Invalid request. 'prompt' is required."}), 400

        # --- Get User Inputs ---
        prompt = data.get('prompt')
        genre = data.get('genre', 'creative')
        length = data.get('length', 'short')
        tone = data.get('tone', 'neutral')
        creativity = float(data.get('creativity', 0.7)) # This will be our temperature

        # --- Improved Prompt Engineering ---
        full_prompt = (
            f"Write a {length} story based on this idea: '{prompt}'.\n\n"
            f"The story should be a {genre} story with a {tone} tone.\n"
            f"Use simple sentences and easy words that a child can understand.\n"
            f"Please only write the story, with nothing else before or after it."
        )
        
        # --- Model Configuration ---
        generation_config = {
            "temperature": creativity,
            "top_p": 0.95,
            "top_k": 64,
            "max_output_tokens": 8192,
        }

        # --- Call the AI Model ---
        model = genai.GenerativeModel(
            # CORRECTED: The model name is now valid.
            model_name="gemini-2.5-flash",
            generation_config=generation_config,
        )

        response = model.generate_content(full_prompt)
        
        clean_story = response.text.strip()
        
        return jsonify({"story": clean_story})

    except Exception as e:
        print(f"An error occurred: {e}")
        return jsonify({"error": "Failed to generate story. Please check the backend logs."}), 500

if __name__ == '__main__':
    # Use 0.0.0.0 to make it accessible on your network
    app.run(host='0.0.0.0', port=5000, debug=True)