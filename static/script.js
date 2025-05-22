// static/script.js
document.addEventListener('DOMContentLoaded', () => {
    const chatMessages = document.getElementById('chat-messages');
    const userInput = document.getElementById('user-input');
    const sendButton = document.getElementById('send-button');

    // Function to add a message to the chat display
    function addMessage(message, sender) {
        const messageDiv = document.createElement('div');
        messageDiv.classList.add('message', `${sender}-message`);
        // Using innerHTML is fine here as we're controlling the content
        // However, for truly raw user input, sanitize before using innerHTML
        messageDiv.innerHTML = `<p>${message}</p>`;
        chatMessages.appendChild(messageDiv);
        // Scroll to the bottom of the chat
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    // Function to add a typing indicator
    function addTypingIndicator() {
        const typingDiv = document.createElement('div');
        typingDiv.classList.add('message', 'bot-message', 'typing-indicator');
        // A simple text indicator for now, can be replaced with an animation
        typingDiv.innerHTML = '<p>Amanda is typing...</p>';
        chatMessages.appendChild(typingDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
        return typingDiv; // Return the element so we can remove it later
    }

    // Function to remove a specific typing indicator
    function removeTypingIndicator(indicator) {
        if (indicator && chatMessages.contains(indicator)) {
            chatMessages.removeChild(indicator);
        }
    }

    // Function to send message to backend
    async function sendMessage() {
        const message = userInput.value.trim();
        if (message === '') return; // Don't send empty messages

        addMessage(message, 'user');
        userInput.value = ''; // Clear input field immediately
        userInput.disabled = true; // Disable input while waiting for response
        sendButton.disabled = true; // Disable send button

        const typingIndicator = addTypingIndicator(); // Add typing indicator

        try {
            const response = await fetch('/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ message: message }),
            });

            if (!response.ok) {
                // If response is not OK (e.g., 400, 500 error)
                const errorText = await response.text(); // Get error message from server if any
                throw new Error(`HTTP error! status: ${response.status}. Details: ${errorText}`);
            }

            const data = await response.json(); // Parse JSON response
            
            removeTypingIndicator(typingIndicator); // Remove typing indicator

            // The bot response from the backend should already be cleaned by chatbot_core.py
            addMessage(data.response, 'bot');

        } catch (error) {
            console.error('Error sending message:', error);
            removeTypingIndicator(typingIndicator); // Remove typing indicator even on error
            addMessage("I'm sorry, I'm having trouble connecting or processing your request. Please try again later.", 'bot');
        } finally {
            // Re-enable input and button regardless of success or failure
            userInput.disabled = false;
            sendButton.disabled = false;
            userInput.focus(); // Put focus back on the input field
        }
    }

    // Event Listeners
    // Ensure the event listener is correctly attached
    sendButton.addEventListener('click', sendMessage);

    userInput.addEventListener('keypress', (event) => {
        if (event.key === 'Enter' && !sendButton.disabled) { // Prevent sending if button is disabled
            sendMessage();
        }
    });

    // Optional: Focus the input field when the page loads
    userInput.focus();
});