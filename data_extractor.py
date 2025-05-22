import google.generativeai as genai
import json
import os
import logging
from dotenv import load_dotenv
import time

# Load environment variables from .env file
load_dotenv()

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def configure_gemini():
    
    try:
        api_key = os.environ.get("myAPiKey")
        if not api_key:
            raise ValueError("Key error in env")
        genai.configure(api_key=api_key)
        logging.info("Config success.")
        return genai.GenerativeModel('gemini-2.0-flash')
    except Exception as e:
        logging.error(f"Error config {e}")
        return None

def generate_info_with_gemini(institute_name, gemini_model, data_schema, additional_context=None):
    """
    Generate structured data about an institution subject to 
     the provided schema.
    """
    if not gemini_model:
        logging.error("Cannot generate information.")
        return None

    # Convert the schema to a JSON string BEFORE embedding it in the prmt.
    schema_json_string = json.dumps(data_schema, indent=2)

    # --- REVISED PROMPT CONSTRUCTION ---
    prompt_lines = [
        "You are an expert at providing structured information about educational institutions.",
        f"Based on your general knowledge, provide details about '{institute_name}' and strictly",
        "adhere to the provided JSON schema. Fill in as much information as possible from your knowledge base.",
        "If a specific piece of information is not available or not clearly known, omit that key or set its",
        "value to null based on the schema's type hints (e.g., \"string | null\").",
        "Ensure all extracted text is concise and relevant.",
        "",
        "For lists (like 'phone_numbers' or 'required_documents'), provide all relevant items you know.",
        "",
        "JSON Schema to follow:",
        "```json",
        schema_json_string, # Insert the pre-formatted JSON 
        "```",
        "",
    ]

    if additional_context:
        prompt_lines.append(f"Additional context for {institute_name}: {additional_context}\n")
    else:
        prompt_lines.append("") # Maintain consistent line break if no context

    prompt_lines.append("Output ONLY the JSON object, formatted exactly as per the schema, with no additional text or markdown outside the JSON block.")

    prompt = "\n".join(prompt_lines)
    # --- END REVISED PROMPT CONSTRUCTION ---

    logging.info(f"Requesting '{institute_name}' data...")
    
    try:
        retries = 3
        for attempt in range(retries):
            try:
                response = gemini_model.generate_content(prompt)
                json_str = response.text.strip()
                
                # Clean up markdown code blocks if Gem wraps the JSON
                if json_str.startswith("```json"):
                    json_str = json_str[len("```json"):].strip()
                if json_str.endswith("```"):
                    json_str = json_str[:-len("```")].strip()
                
                extracted_data = json.loads(json_str)
                logging.info(f"Successfully generated data for '{institute_name}'.")
                return extracted_data
            except json.JSONDecodeError as e:
                logging.error(f"Attempt {attempt+1}: Error decoding JSON for '{institute_name}': {e}")
                logging.error(f"Raw Gem data: \n{json_str[:500]}...")
                time.sleep(2)
            except Exception as e:
                logging.error(f"Attempt {attempt+1}: Error in call for '{institute_name}': {e}")
                if response and hasattr(response, 'text'):
                    logging.error(f"Raw response: {response.text[:500]}...")
                time.sleep(2)
        logging.error(f"Failed to generate data for '{institute_name}' after {retries} attempts.")
        return None

    except Exception as e:
        logging.error(f"An unexpected error occurred before calling for '{institute_name}': {e}")
        return None

def main():
    gemini_model = configure_gemini()
    if not gemini_model:
        return

    # Define your generic JSON schema for university data
    # THIS SCHEMA IS CRITICAL. ADJUST IT TO PERFECTLY MATCH THE DATA YOU WANT TO EXTRACT.
    university_data_schema = {
        "institute_name": "string",
        "university_overview": {
            "motto": "string | null",
            "vision": "string | null",
            "mission": "string | null",
            "general_overview": "string | null",
            "location": {
                "city": "string | null",
                "county": "string | null",
                "country": "string | null",
                "coordinates": "string | null"
            },
            "vice_chancellor": {
                "name": "string | null"
            },
            "establishment_year": "string | null",
            "type": "string | null"
        },
        "admissions_general": {
            "undergraduate_programs": {
                "general_requirements": {
                    "kenyan_students": {
                        "kcse_minimum": "string | null",
                        "diploma_entry_requirements": "string | null"
                    },
                    "international_students": {
                        "equivalent_qualifications": "string | null"
                    }
                },
                "application_process": {
                    "required_documents": "list of strings | null",
                    "application_portal_link": "string | null",
                    "application_deadlines": "string | null"
                }
            },
            "postgraduate_programs": {
                "general_requirements": "string | null"
            }
        },
        "fees_information": {
            "tuition_and_fees": {
                "general_information": "string | null",
                "common_fee_structures": {
                    "government_sponsored_students": {
                        "approximate_fee_range_per_year_kes": "string | null"
                    },
                    "self_sponsored_students": {
                        "approximate_fee_range_per_year_kes": "string | null"
                    },
                    "international_students": {
                        "approximate_fee_range_per_year_usd": "string | null"
                    }
                }
            }
        },
        "contact_details": {
            "main_contact_information": {
                "general_enquiries": {
                    "phone_numbers": "list of strings | null",
                    "email": "string | null"
                },
                "admissions_office": {
                    "phone_numbers": "list of strings | null",
                    "email": "string | null"
                },
                "physical_address": "string | null"
            }
        },
        "admission_faqs": [
            {
                "question": "string",
                "answer": "string"
            }
        ],
        "courses_offered": [
            {
                "course_name": "string",
                "degree_level": "string | null",
                "duration": "string | null",
                "fees_kes": "string | null",
                "entry_requirements": "string | null",
                "department": "string | null"
            }
        ],
        "campus_facilities": {
            "libraries": "string | null",
            "hostels_accommodation": "string | null",
            "sports_facilities": "string | null",
            "health_services": "string | null"
        },
        "student_life": {
            "clubs_societies": "string | null",
            "events_traditions": "string | null"
        },
        "research_innovation": {
            "key_research_areas": "list of strings | null",
            "research_centers": "list of strings | null",
            "publications_highlights": "string | null"
        },
        "alumni_relations": {
            "alumni_association_info": "string | null"
        },
        "rankings_accreditations": {
            "national_rankings": "string | null",
            "international_rankings": "string | null",
            "accrediting_bodies": "list of strings | null"
        }
    }

    # --- Configuration for Institutions to Generate Data For ---
    institute_configs = {
        "JKUAT": {
            "name": "Jomo Kenyatta University of Agriculture and Technology",
            "output_file": "data/jkuat_data.json",
            "additional_context": "Focus on general details, admissions for Kenyan students, common fees, and primary contact details."
        },
        # Example for another institution (uncomment and fill in if you want to test)
        # "UoN": {
        #     "name": "University of Nairobi",
        #     "output_file": "data/uon_data.json",
        #     "additional_context": "Highlight their main campus, popular courses, and a brief history."
        # }
    }

    # Process each configured institution
    for key, config in institute_configs.items():
        institute_name = config["name"]
        output_file = config["output_file"]
        additional_context = config.get("additional_context")
        
        logging.info(f"\n--- Generating data for {institute_name} ---")
        
        extracted_data = generate_info_with_gemini(institute_name, gemini_model, university_data_schema, additional_context)

        if extracted_data:
            # Add the institute name to the extracted data at the top level
            extracted_data["institute_name"] = institute_name 
            
            output_dir = os.path.dirname(output_file)
            if output_dir and not os.path.exists(output_dir):
                os.makedirs(output_dir, exist_ok=True)
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(extracted_data, f, indent=2, ensure_ascii=False)
            logging.info(f"Successfully generated and saved data for {institute_name} to {output_file}")
        else:
            logging.error(f"Failed to generate data for {institute_name}.")

if __name__ == "__main__":
    main()