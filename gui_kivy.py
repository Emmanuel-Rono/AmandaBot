from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.core.window import Window
from kivy.clock import mainthread
import threading
import logging

# Config logging for Kivy messages
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class ChatbotApp(App):
    def __init__(self, chatbot_core_instance, **kwargs):
        super().__init__(**kwargs)
        self.bot = chatbot_core_instance
        self.title = f"Amanda: Smart Enquiry Chatbot for {self.bot.institution_name}"

    def build(self):
        # window size
        Window.size = (700, 600) 

        # Main layout
        self.main_layout = BoxLayout(orientation='vertical', padding=10, spacing=10)

        # Chat history display
        self.history_label = Label(text="", size_hint_y=None, valign='top', markup=True)
        self.history_label.bind(texture_size=self.history_label.setter('size')) # Automatically adjust height

        self.scroll_view = ScrollView(size_hint=(1, 0.85)) 
        self.scroll_view.add_widget(self.history_label)
        self.main_layout.add_widget(self.scroll_view)

        # Input box
        self.input_box = TextInput(
            hint_text="Type your question here...",
            multiline=False,
            size_hint_y=None,
            height=40,
            font_size=18,
            padding_x=10,
            padding_y=[8, 0], 
            background_color=[0.95, 0.95, 0.95, 1], 
            foreground_color=[0, 0, 0, 1], # Black text
            cursor_color=[0, 0, 0, 1] # Black cursor
        )
        self.input_box.bind(on_text_validate=self.send_message) # Send on Enter key
        self.main_layout.add_widget(self.input_box)

        # Send button
        self.send_button = Button(
            text="Send",
            size_hint_y=None,
            height=50,
            font_size=20,
            background_normal='', # Remove default Kivy button look
            background_color=[0.2, 0.6, 0.8, 1], # Blue color
            color=[1, 1, 1, 1] # White text
        )
        self.send_button.bind(on_press=self.send_message)
        self.main_layout.add_widget(self.send_button)

        # Initial message from bot
        self.add_message("Amanda", f"Hello! I am Amanda, your smart enquiry chatbot for {self.bot.institution_name}. How can I help you today?", color='#0000FF') # Blue for bot
        
        return self.main_layout

    def add_message(self, sender, message, color='#000000'): # Default black for user
        """Adds a message to the chat history."""
        # Use markup for coloring sender
        new_text = f"[b][color={color}]{sender}[/color][/b]: {message}\n"
        self.history_label.text += new_text
        # Scroll to bottom after adding message
        self.scroll_view.scroll_y = 0

    def send_message(self, instance):
        """Handles sending a user message."""
        user_text = self.input_box.text.strip()
        if not user_text:
            return

        self.add_message("You", user_text, color='#008000') # Green for user
        self.input_box.text = "" # Clear input box

        # Disable input while processing
        self.input_box.disabled = True
        self.send_button.disabled = True
        self.send_button.text = "Thinking..."

        # Run chatbot response in a separate thread to avoid freezing GUI
        threading.Thread(target=self._get_bot_response_thread, args=(user_text,)).start()

    @mainthread
    def _update_gui_with_bot_response(self, bot_response):
        """Updates the GUI with the bot's response."""
        self.add_message("Amanda", bot_response, color='#0000FF') # Blue for bot
        self.input_box.disabled = False
        self.send_button.disabled = False
        self.send_button.text = "Send"
        self.input_box.focus = True # Put focus back on input box

    def _get_bot_response_thread(self, user_text):
        """Worker thread to get bot response."""
        try:
            bot_response = self.bot.get_response(user_text)
        except Exception as e:
            logging.error(f"Error getting bot response: {e}")
            bot_response = "I encountered an error trying to process your request."
        finally:
            self._update_gui_with_bot_response(bot_response)