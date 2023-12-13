# Gemini Discord Bot

Gemini is an advanced Discord bot that leverages the power of Google's GeminiPro to interact with users in both text and image formats. It processes messages and images sent to it, generating creative and engaging responses.

## Features

- **AI-Driven Text Responses:** Gemini Bot can generate text responses to messages using Google's generative AI.
- **Image Processing:** The bot can also respond to images, combining text and visual inputs for a more engaging interaction.
- **User Message History Management:** It maintains a history of user interactions via discordIDs, allowing for context-aware conversations.
- **Customizable Settings:** Users can adjust various parameters like message history length and AI response settings.

## Setup

### Requirements

- Python 3.6 or higher
- discord.py
- aiohttp
- Google's generativeai library


### Installation

1. Clone the repository to your local machine.
2. Install the required Python libraries:

   ```
   pip install discord.py aiohttp google-generativeai
   ```
The bot will start listening to messages in your Discord server. It responds to direct mentions or direct messages.

## Configuration

Edit the `GeminiBotConfig.py` file must include:

- `DISCORD_BOT_TOKEN`: Your Discord bot token.
- `GOOGLE_AI_KEY`: Your Google AI API key. Google API Key can be acquired from https://makersuite.google.com/
- `MAX_HISTORY`: The maximum number of messages to retain in history for each user. 0 will disable history

then run `GeminiDiscordBot.py`

## Commands

- **Mention or DM the bot to activate:** History only works on pure text input 
- **Send an Image:** The bot will respond with an AI-generated interpretation or related content.
- **Type 'RESET':** Clears the message history for the user.

## Development

Feel free to fork the project and customize it according to your needs. Make sure to follow the guidelines set by Discord and Google for bot development and API usage.
