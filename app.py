# app.py
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS 
import os
import json
import logging
from dotenv import load_dotenv

# Import  ChatbotCore
from chatbot_core import ChatbotCore 

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

app = Flask(__name__, static_folder='static') 
CORS(app) 

# --- Initialize ChatbotCorewhen the app starts ---
chatbot = None 

@app.before_request
def initialize_chatbot():
    global chatbot
    if chatbot is None:
        try:
            aiml_path = 'aiml_files'
            jkuat_data_path = 'data/jkuat_data.json' 
            gemini_api_key = os.environ.get("myAPiKey")

            chatbot = ChatbotCore(aiml_path=aiml_path)

            # Load institution data
            if os.path.exists(jkuat_data_path):
                with open(jkuat_data_path, 'r', encoding='utf-8') as f:
                    jkuat_data = json.load(f)
                chatbot.set_institution_data(jkuat_data, name="JKUAT")
            else:
                logging.warning(f"JKUAT data file not found at {jkuat_data_path}")

            logging.info("ChatbotCore initialized successfully.")

        except Exception as e:
            logging.error(f"Failed to initialize ChatbotCore: {e}")
           

@app.route('/')
def index():
    """Renders the main chatbot HTML page."""
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    """Handles chat messages from the frontend."""
    if chatbot is None:
        logging.error("Chatbot not initialized. Cannot process request.")
        return jsonify({"response": "Error: Chatbot is not ready. Please check server logs."}), 500

    user_message = request.json.get('message')
    if not user_message:
        return jsonify({"response": "No message provided."}), 400

    logging.info(f"User: {user_message}")
    bot_response = chatbot.get_response(user_message)
    logging.info(f"Bot: {bot_response}")

    return jsonify({"response": bot_response})

if __name__ == '__main__':
    # Ensure the 'data' directory exists
    if not os.path.exists('data'):
        os.makedirs('data')
        logging.info("Created 'data' directory.")


    if not os.path.exists('data/jkuat_data.json'):
        logging.warning("jkuat_data.json not found.")

    app.run(debug=True, port=5000) # debug=True  Disable in production