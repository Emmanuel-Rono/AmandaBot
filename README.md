# Amanda Chatbot
Amanda Chatbot is **Python-based chatbot** built for JKUAT, providing instant access to university information. 
It employs AIML for robust conversational flows and NLTK for natural language understanding.
Designed with modularity in mind, this system can be readily adapted to serve as an informational assistant for any institution by simply updating its structured knowledge base and conversational rules.


---

## Scalability & Adaptation

While currently tailored for JKUAT, this chatbot's architecture is inherently **scalable and adaptable** for other institutions. The design emphasizes a clear separation between the core chatbot logic and the institution-specific data and rules.

To repurpose this chatbot for a different university or organization:

1.  **Update `data/ :** Folder with your institution's data in JSON:
2.  **Modify `aiml_files/:** Adjust or create new AIML patterns and templates to match common queries and desired responses for the new institution.

This modular design allows for significant re-use of the core chatbot logic, minimizing code changes when adapting it to a new knowledge domain.

---

## Installation & Run Steps

Here’s how to get the JKUAT Chatbot up and running quickly:

1.  **Clone the repository:**
    ```bash
    git clone  https://github.com/Emmanuel-Rono/AmandaBot
    cd AmandaBot
    ```
2.  **Install dependencies:** It's a good idea to use a virtual environment.
    ```bash
    python -m venv venv
    # On Windows: .\venv\Scripts\activate
    # On macOS/Linux: source venv/bin/activate
    pip install -r requirements.txt
    # If requirements.txt is missing, install manually:
    # pip install nltk python-aiml kivy google-generativeai
    ```
3.  **Download NLTK data:** The `chatbot_core.py` aims to do this automatically, but if you hit issues, you can run:
    ```python
    python -c "import nltk; nltk.download('punkt'); nltk.download('wordnet'); nltk.download('stopwords'); nltk.download('omw-1.4'); nltk.download('punkt_tab')"
    ```
4.  **Ensure `data/institution_data.json` exists** and is populated with your institution's information. This is your primary knowledge base.
5.  **Delete `aiml_files/brain.brn`** if it exists. This ensures the chatbot loads any fresh data and AIML rules on startup.
    ```bash
    # On macOS/Linux
    rm aiml_files/brain.brn
    # On Windows
    del aiml_files\brain.brn
    ```
6.  **Run the application:**
    ```bash
    python main.py
    ```

---
