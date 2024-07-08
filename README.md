# Gemini Discord Bot

 Discord bot that leverages the power of Google's Gemini-Pro API to interact with users in both text and image formats. It processes messages and images sent to it, generating creative and engaging responses. 

# UPDATE

This Gemini bot now is running Gemini Flash 1.5, PDF's and text files are now supported along with parsing transcripts from youtube videos and scraping of text from URLs.

The original bot that just does text and images is under `GeminiSimple.py`, If you don't want the extra capabilities and want to make something new.

## Features

- **AI-Driven Text Responses:** Gemini Bot can generate text responses to messages using Google's generative AI.
- **Image Processing:** The bot can also respond to images, combining text and visual inputs for a more engaging interaction. (Images should be under 2.5 Megs)
- **User Message History Management:** It maintains a history of user interactions via discordIDs, allowing for context-aware conversations.
- **Customizable Settings:** Users can adjust various parameters like message history length and AI response settings.

## Setup

### Requirements

- aiohttp
- discord.py
- google-generativeai
- python-dotenv
- youtube-transcript-api (yutube transcript_
- discord.py
- google-generativeai
- aiohttp
- PyMuPDF (PDF reading)
- requests
- beautifulsoup4 (scraping)
- python-dotenv

  Recently updated to use Google Flash 1.5 you may need to update your python package

  ```
  pip install --upgrade google-generativeai

  ```


### Installation

1. Clone the repository to your local machine.
2. Install the required Python libraries:

   ```
   pip install -U -r requirements.txt
   ```
The bot will start listening to messages in your Discord server. It responds to direct mentions or direct messages.

## Configuration

1. Create a `.env` file and copy the contents of `.env.example` into it

2. Fill in the following values:

- `DISCORD_BOT_TOKEN`: Your Discord bot token
- `GOOGLE_AI_KEY`: Your Google AI API key. Google API Key can be acquired from https://makersuite.google.com/
- `MAX_HISTORY`: The maximum number of messages to retain in history for each user. 0 will disable history

3. Run `GeminiDiscordBot.py`


## Commands

- **Mention or DM the bot to activate:** History only works on pure text input
- **Send an Image:** The bot will respond with an AI-generated interpretation or related content.
- **Type 'RESET' or CLEAN :** Clears the message history for the user.

## Additional Items 

- Youtube URLs - Read's the transcript from a youtube video and you can ask a question about it
- PDF / TXT - PDF or TXT will be added into your prompt
- Web URL - It will scrape the text off a URL (As well as it can)

You can preprompt your request just like with images. If you just paste a URL and no context it default to the `SUMMERIZE_PROMPT` which is set to `Give me 5 Bullets about` feel free to change this in the code

Examples:
`Write me a tweet about {url}`
`What did they think of {youtubeVideo transcript}`

The system_prompt for Gemini Flash has been commented out just uncomment if you want to use it.


## Development

Feel free to fork the project and customize it according to your needs. Make sure to follow the guidelines set by Discord and Google for bot development and API usage.

## Limitations

Web Urls: 
- Google docs URLs don't parse correctly
- Some URLs will not parse correctly 
Youtube Videos
- Transcripts of age restricted or other block content cannot be read
