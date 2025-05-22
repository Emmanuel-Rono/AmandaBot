import nltk
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords
import aiml
import os
import json
import logging
from dotenv import load_dotenv 
import re 
import google.generativeai as genai 

# environment variables 
load_dotenv()

# Configure logging 
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Helper function to clean Responses
def clean_gemini_response_text(text):
  
    # Remove bolding (**text**) and italics (*text*)
    text = re.sub(r'\*\*(.*?)\*\*', r'\1', text) # Removes ** and **
    text = re.sub(r'\*(.*?)\*', r'\1', text)    # Removes * and * (after bolding removed)

    # Remove markdown list markers 
    # handles leading whitespace
    text = re.sub(r'^\s*[-*+]?\s*\d*\.?\s*', '', text, flags=re.MULTILINE)

    # Replace multiple newlines 
    text = re.sub(r'\n{3,}', '\n\n', text)

    # Strip leading/trailing whitespace 
    text_lines = [line.strip() for line in text.split('\n')]
    text = '\n'.join(text_lines).strip()

    return text



# Config Gem's
_global_gemini_model = None
try:
    api_key = os.environ.get("myAPiKey")
    if not api_key:
        raise ValueError("environment variable not set")
    genai.configure(api_key=api_key)
    
    available_models = [
        m for m in genai.list_models()
        if 'generateContent' in m.supported_generation_methods and 'gemini-2.0-flash' in m.name
    ]
    if available_models:
        _global_gemini_model = genai.GenerativeModel(available_models[0].name)
        logging.info("[GLOBAL] API configured successfully ")
    else:
        logging.warning("Change Mdel")

except Exception as e:
    logging.warning(f" Error  global configuration")
    _global_gemini_model = None


class ChatbotCore:
    def __init__(self, aiml_path='aiml_files'):
        self._download_nltk_data()

        self.lemmatizer = WordNetLemmatizer()
        self.stop_words = set(stopwords.words('english'))
        self.aiml_kernel = aiml.Kernel()

        self.aiml_path = aiml_path
        self.institution_data = {} 
        self.institution_name = "the institution" # Default placeholder

        self._load_aiml_brain()
        
        # Link to the globally configured  model
        self.gemini_model = _global_gemini_model 

    def _download_nltk_data(self):
        """Helper to download necessary NLTK data."""
        nltk_packages = ['punkt', 'wordnet', 'stopwords', 'omw-1.4', 'punkt_tab']
        for package in nltk_packages:
            try:
                # Adjust path for punkt_tab specifically if needed, otherwise general
                if package == 'punkt_tab':
                    nltk.data.find(f'tokenizers/{package}')
                else:
                    nltk.data.find(f'corpora/{package}')
            except LookupError:
                logging.info(f"[NLTK] Downloading necessary NLTK data: {package}...")
                nltk.download(package, quiet=True)
                logging.info(f"[NLTK] {package} download complete.")

    def set_institution_data(self, data, name="Default Institution"):
        """
        Sets the institution-specific data for the chatbot.
        This method replaces the internal _load_jkuat_data.
        """
        self.institution_data = data
        self.institution_name = name
        logging.info(f"[ChatbotCore] Data for '{self.institution_name}' loaded and set.")
        self._set_institution_predicates_for_aiml()

    def _load_aiml_brain(self):
        # Resolve the full absolute path for the brain file BEFORE changing directory
        brain_file_abs_path = os.path.join(os.getcwd(), self.aiml_path, 'brain.brn')

        # Temporarily change current directory to AIML path for kernel.learn() to find files
        current_dir = os.getcwd()
        os.chdir(self.aiml_path)

        try:
            if os.path.exists('brain.brn'):
                logging.info(f"[ChatbotCore] Loading AIML brain from: {brain_file_abs_path}")
                self.aiml_kernel.loadBrain('brain.brn')
            else:
                logging.info("[ChatbotCore] No saved brain found. Loading AIML files...")
                for file in os.listdir("."):
                    if file.endswith(".aiml"):
                        logging.info(f"    Learning {file}...")
                        self.aiml_kernel.learn(file)

                logging.info("[ChatbotCore] Saving AIML brain for faster future loading...")
                try:
                    self.aiml_kernel.saveBrain('brain.brn')
                    logging.info("[ChatbotCore] Brain saved successfully.")
                except Exception as e:
                    logging.error(f"Error saving AIML brain to 'brain.brn' (inside {self.aiml_path}): {e}")
                    logging.warning("Means the brain won't be loaded faster next time, but the chatbot should still function.")
        except Exception as e:
            logging.error(f"[ChatbotCore] ERROR during AIML brain loading: {e}")
            logging.error("Check your AIML files for syntax errors ")
        finally:
            os.chdir(current_dir)

        logging.info("[ChatbotCore] AIML brain loaded successfully!")

    def _set_institution_predicates_for_aiml(self):
        """
        Sets institution data as AIML bot predicates 
        """
        logging.info(f"[ChatbotCore] Setting predicates for '{self.institution_name}'...")

        # Set the main institution name predicate
        self.aiml_kernel.setBotPredicate("institution_name", self.institution_name)

        # Overview Data
        overview = self.institution_data.get('university_overview', {})
        self.aiml_kernel.setBotPredicate("institution_motto", overview.get('motto', 'Information not found.'))
        self.aiml_kernel.setBotPredicate("institution_vision", overview.get('vision', 'Information not found.'))
        self.aiml_kernel.setBotPredicate("institution_mission", overview.get('mission', 'Information not found.'))
        self.aiml_kernel.setBotPredicate("institution_general_overview", overview.get('general_overview', 'Information not found.'))

        location_dict = overview.get('location', {})
        if isinstance(location_dict, dict):
            city = location_dict.get('city', 'N/A')
            county = location_dict.get('county', 'N/A')
            country = location_dict.get('country', 'N/A')
            coordinates = location_dict.get('coordinates', '')
            full_location_string = f"{city}, {county}, {country}"
            if coordinates and coordinates not in ['N/A', '']:
                full_location_string += f" ({coordinates})"
            self.aiml_kernel.setBotPredicate("institution_location", full_location_string)
        else:
            self.aiml_kernel.setBotPredicate("institution_location", location_dict if location_dict else 'Information not found.')

        vc_data = overview.get('vice_chancellor', {})
        if isinstance(vc_data, dict):
            vc_name = vc_data.get('name', 'Information not found.')
            self.aiml_kernel.setBotPredicate("institution_vice_chancellor", vc_name)
        else:
            self.aiml_kernel.setBotPredicate("institution_vice_chancellor", vc_data if vc_data else 'Information not found.')


        # Admissions Data
        admissions = self.institution_data.get('admissions_general', {})
        ug_reqs = admissions.get('undergraduate_programs', {}).get('general_requirements', {})
        kenyan_ug_reqs = ug_reqs.get('kenyan_students', {})
        admission_requirements_str = kenyan_ug_reqs.get('kcse_minimum', 'N/A')
        self.aiml_kernel.setBotPredicate("institution_admission_requirements", admission_requirements_str)

        app_process = admissions.get('undergraduate_programs', {}).get('application_process', {})
        docs_required = app_process.get('required_documents', [])
        if isinstance(docs_required, list) and docs_required:
            self.aiml_kernel.setBotPredicate("institution_admission_documents_required", "You will typically need: " + ", ".join(docs_required) + ".")
        else:
            self.aiml_kernel.setBotPredicate("institution_admission_documents_required", "Information on required documents is currently unavailable.")

        # Fees Information
        fees_info = self.institution_data.get('fees_information', {})
        tuition_fees = fees_info.get('tuition_and_fees', {})
        fees_description_parts = []
        general_info = tuition_fees.get('general_information', "Please check the official institution fees page for comprehensive details.")
        fees_description_parts.append(general_info)

        gov_fees = tuition_fees.get('common_fee_structures', {}).get('government_sponsored_students', {})
        if gov_fees.get('approximate_fee_range_per_year_kes'):
            fees_description_parts.append(f"For government-sponsored students, approximate annual fees: KES {gov_fees['approximate_fee_range_per_year_kes']}.")

        self_fees = tuition_fees.get('common_fee_structures', {}).get('self_sponsored_students', {})
        if self_fees.get('approximate_fee_range_per_year_kes'):
            fees_description_parts.append(f"For self-sponsored students, approximate annual fees: KES {self_fees['approximate_fee_range_per_year_kes']}.")

        int_fees = tuition_fees.get('common_fee_structures', {}).get('international_students', {})
        if int_fees.get('approximate_fee_range_per_year_usd'):
            fees_description_parts.append(f"For international students, approximate annual fees (USD): {int_fees['approximate_fee_range_per_year_usd']}.")

        final_fees_description = " ".join(fees_description_parts)
        self.aiml_kernel.setBotPredicate("institution_fees_info", final_fees_description)

        # Contact Details
        contacts = self.institution_data.get('contact_details', {})
        general_enquiries = contacts.get('main_contact_information', {}).get('general_enquiries', {})
        admissions_office = contacts.get('main_contact_information', {}).get('admissions_office', {})

        self.aiml_kernel.setBotPredicate("institution_general_phone", ", ".join(general_enquiries.get('phone_numbers', ['N/A'])))
        self.aiml_kernel.setBotPredicate("institution_general_email", general_enquiries.get('email', 'N/A'))
        self.aiml_kernel.setBotPredicate("institution_admissions_phone", ", ".join(admissions_office.get('phone_numbers', ['N/A'])))
        self.aiml_kernel.setBotPredicate("institution_admissions_email", admissions_office.get('email', 'N/A'))

        # FAQs
        admission_faqs = self.institution_data.get('admission_faqs', [])
        if admission_faqs:
            faq_summary = ""
            for i, qa in enumerate(admission_faqs[:3]): # Limiting to 3 for summary
                faq_summary += f"\n{i+1}. Q: {qa.get('question', '')}\n   A: {qa.get('answer', '')}"
            self.aiml_kernel.setBotPredicate("institution_admission_faqs_summary", faq_summary)
        else:
            self.aiml_kernel.setBotPredicate("institution_admission_faqs_summary", "No specific admission FAQs available at the moment.")

        logging.info("[ChatbotCore] Institution predicates set.")

    def preprocess_text(self, text):
        """Converts text to uppercase, removes stop words, and lemmatizes."""
        text = text.upper()
        words = nltk.word_tokenize(text)
        upper_stop_words = {word.upper() for word in self.stop_words}
        filtered_words = []
        for word in words:
            lemmatized_word = self.lemmatizer.lemmatize(word)
            if lemmatized_word.upper() not in upper_stop_words:
                if lemmatized_word.isalnum(): 
                    filtered_words.append(lemmatized_word)
        return " ".join(filtered_words)

    def get_response(self, user_input):
        """Gets a response from the chatbot based on user input."""
        # Process user input for AIML matching
        processed_input = self.preprocess_text(user_input)
        logging.debug(f"Processed input for AIML: '{processed_input}'")

        # First,get a response from AIML 
        response = self.aiml_kernel.respond(processed_input)

        # fallback plan
        if not response or response.strip() == "":
            logging.info("Consulting ...")
            if self.gemini_model:
                try:
                    gemini_prompt = (
                        f"You are the official JKUAT School Chatbot. Your purpose is to assist students "
                        f"by providing concise, factual information about JKUAT. "
                        f"Always use available information. Avoid stating 'I don't know'.\n\n" 
                        f"Provide a direct, concise answer to the following question. "
                        f"If a list or explanation is requested, limit it to under 100 words. "
                        f"Question: {user_input}"
                        )    
                    gemini_raw_response_obj = self.gemini_model.generate_content(gemini_prompt) # Use the new prompt
                    
                    if hasattr(gemini_raw_response_obj, 'text') and gemini_raw_response_obj.text:
                        response_text = gemini_raw_response_obj.text
                        # --- APPLY THE CLEANING FUNCTION HERE! ---
                        response = clean_gemini_response_text(response_text)
                        logging.info("[ChatbotCore] Got it.")
                    else:
                        logging.warning("[ChatbotCore] Not Response.")
                        response = "I couldn't process at the moment"
                except Exception as e:
                    logging.error(f"[ChatbotCore] ERROR calling Assistant: {e}")
                    response = "I'm sorry, I couldn't get an answer at the moment"
            else:
                response = f"I'm sorry, I don't have information on that about {self.institution_name},Can you try asking about something else related to {self.institution_name}?"

        return response