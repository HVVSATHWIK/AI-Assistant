document.addEventListener("DOMContentLoaded", () => {
  const sendButton = document.getElementById('send-button');
  const userInput = document.getElementById('user-input');
  const chatLog = document.getElementById('chat-log');

  sendButton.addEventListener('click', () => {
    const userMessage = userInput.value .trim();
    if (userMessage) {
      displayMessage(userMessage, 'user');
      userInput.value = '';
      getAIResponse(userMessage);
    }
  });
  
  userInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') {
      sendButton.click();
    }
  });

  function displayMessage(message, sender) {
    const messageDiv = document.createElement('div');
    messageDiv.classList.add('message', `${sender}-message`);
    const textDiv = document.createElement('div');
    textDiv.classList.add('text');
    textDiv.innerText = message;
    messageDiv.appendChild(textDiv);
    chatLog.appendChild(messageDiv);
    chatLog.scrollTop = chatLog.scrollHeight;
  }

  async function getAIResponse(userMessage) {
    try {
      const response = await fetch('/get_response', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ user_input: userMessage })
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      displayMessage(data.response, 'ai');
    } catch (error) {
      console.error('Error fetching AI response:', error);
      displayMessage("Sorry, there was an error processing your request.", 'ai');
    }
  }
});
