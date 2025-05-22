import os
import json
import logging
from chatbot_core import ChatbotCore
from gui_kivy import ChatbotApp

# Configure logging for the main script
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def load_institution_json(filepath):
    """Helper function to load institution data from a JSON file."""
    if os.path.exists(filepath):
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
                logging.info(f"Successfully loaded institution data from {filepath}")
                return data
        except json.JSONDecodeError as e:
            logging.error(f"Error: Invalid JSON format in {filepath}: {e}")
            return None
        except Exception as e:
            logging.error(f"An unexpected error occurred while loading {filepath}: {e}")
            return None
    logging.error(f"Error: Institution data file not found at {filepath}")
    return None

if __name__ == "__main__":
    logging.info("--- Starting Amanda Chatbot Application ---")

    # Define paths
    AIML_PATH = 'aiml_files'
    DATA_DIR = 'data'
    JKUAT_DATA_FILE = os.path.join(DATA_DIR, 'jkuat_data.json')


    os.makedirs(DATA_DIR, exist_ok=True)

    # Initialize chatbot core
    chatbot_instance = ChatbotCore(aiml_path=AIML_PATH)

    # --- Load specific institution data ---
    #  Hardcoding JKUAT for the initial load
    
    institution_name_for_load = "Jomo Kenyatta University of Agriculture and Technology"
    
    institution_data = load_institution_json(JKUAT_DATA_FILE)

    if institution_data:
        chatbot_instance.set_institution_data(institution_data, name=institution_name_for_load)
        logging.info(f"Chatbotnow configured for {chatbot_instance.institution_name}.")
    else:
        logging.critical(f"Failed to load data for {institution_name_for_load}."
                         f"Do'{JKUAT_DATA_FILE}' exists ? " )
                         
        # Optionally exit or handle this gracefully in the GUI
        exit("Chatbot cannot start without institution data.")

    # Run the Kivy GUI application
    ChatbotApp(chatbot_core_instance=chatbot_instance).run()
    logging.info("--- Amanda Chatbot Application Exited ---")