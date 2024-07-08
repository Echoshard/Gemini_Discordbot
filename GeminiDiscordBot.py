import discord
import google.generativeai as genai
from discord.ext import commands
from pathlib import Path
import aiohttp
import re
import os
import fitz  # PyMuPDF
import asyncio

#Web Scraping
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv

load_dotenv()
GOOGLE_AI_KEY = os.getenv("GOOGLE_AI_KEY")
DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
MAX_HISTORY = int(os.getenv("MAX_HISTORY"))

#Default Summary Prompt if you just shove a URL in
SUMMERIZE_PROMPT = "Give me 5 bullets about"

message_history = {}


#show_debugs = False

#---------------------------------------------AI Configuration-------------------------------------------------

# Configure the generative AI model
genai.configure(api_key=GOOGLE_AI_KEY)
text_generation_config = {
    "temperature": 0.9,
    "top_p": 1,
    "top_k": 1,
    "max_output_tokens": 512,
}

safety_settings = [
    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_ONLY_HIGH"},
    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_ONLY_HIGH"},
    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_ONLY_HIGH"},
    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_ONLY_HIGH"}
]

gemini_model = genai.GenerativeModel(model_name="gemini-1.5-flash", generation_config=text_generation_config, safety_settings=safety_settings)

# Uncomment these if you want to use the system prompt but it's a bit weird
# gemini_system_prompt = ""
# gemini_model = genai.GenerativeModel(model_name="gemini-1.5-flash", generation_config=text_generation_config, safety_settings=safety_settings,system_instruction=gemini_system_prompt)

#---------------------------------------------Discord Code-------------------------------------------------
# Initialize Discord bot
defaultIntents = discord.Intents.default()
defaultIntents.message_content = True
bot = commands.Bot(command_prefix="!", intents=defaultIntents)

@bot.event
async def on_ready():
    print("----------------------------------------")
    print(f'Gemini Bot Logged in as {bot.user}')
    print("----------------------------------------")
    
@bot.event
async def on_message(message):
    #Start the coroutine
    asyncio.create_task(process_message(message))

#----This is now a coroutine for longer messages so it won't block the on_message thread
async def process_message(message):
    # Ignore messages sent by the bot or if mention everyone is used
    if message.author == bot.user or message.mention_everyone:
        return

    # Check if the bot is mentioned or the message is a DM
    if bot.user.mentioned_in(message) or isinstance(message.channel, discord.DMChannel):
        # Start Typing to seem like something happened
        cleaned_text = clean_discord_message(message.content)
        async with message.channel.typing():
            # Check for image attachments
            if message.attachments:
                # Currently no chat history for images
                for attachment in message.attachments:
                    print(f"New Image Message FROM: {message.author.name} : {cleaned_text}")
                    # these are the only image extensions it currently accepts
                    if any(attachment.filename.lower().endswith(ext) for ext in ['.png', '.jpg', '.jpeg', '.gif', '.webp']):
                        print("Processing Image")
                        await message.add_reaction('🎨')
                        async with aiohttp.ClientSession() as session:
                            async with session.get(attachment.url) as resp:
                                if resp.status != 200:
                                    await message.channel.send('Unable to download the image.')
                                    return
                                image_data = await resp.read()
                                response_text = await generate_response_with_image_and_text(image_data, cleaned_text)
                                await split_and_send_messages(message, response_text, 1700)
                                return
                    else:
                        print(f"New Text Message FROM: {message.author.name} : {cleaned_text}")
                        await ProcessAttachments(message, cleaned_text)
                        return
            # Not an Image, check for text responses
            else:
                print(f"New Message Message FROM: {message.author.name} : {cleaned_text}")
                # Check for Reset or Clean keyword
                if "RESET" in cleaned_text or "CLEAN" in cleaned_text:
                    # End back message
                    if message.author.id in message_history:
                        del message_history[message.author.id]
                    await message.channel.send("🧼 History Reset for user: " + str(message.author.name))
                    return
                # Check for URLs
                if extract_url(cleaned_text) is not None:
                    await message.add_reaction('🔗')
                    print(f"Got URL: {extract_url(cleaned_text)}")
                    response_text = await ProcessURL(cleaned_text)
                    await split_and_send_messages(message, response_text, 1700)
                    return
                # Check if history is disabled, just send response
                await message.add_reaction('💬')
                if MAX_HISTORY == 0:
                    response_text = await generate_response_with_text(cleaned_text)
                    # Add AI response to history
                    await split_and_send_messages(message, response_text, 1700)
                    return
                # Add user's question to history
                update_message_history(message.author.id, cleaned_text)
                response_text = await generate_response_with_text(get_formatted_message_history(message.author.id))
                # Add AI response to history
                update_message_history(message.author.id, response_text)
                # Split the Message so discord does not get upset
                await split_and_send_messages(message, response_text, 1700)


       
#---------------------------------------------AI Generation History-------------------------------------------------           

async def generate_response_with_text(message_text):
    try:
        prompt_parts = [message_text]
        response = gemini_model.generate_content(prompt_parts)
        if response._error:
            return "❌" + str(response._error)
        return response.text
    except Exception as e:
        return "❌ Exception: " + str(e)

async def generate_response_with_image_and_text(image_data, text):
    try:
        image_parts = [{"mime_type": "image/jpeg", "data": image_data}]
        prompt_parts = [image_parts[0], f"\n{text if text else 'What is this a picture of?'}"]
        response = gemini_model.generate_content(prompt_parts)
        if response._error:
            return "❌" + str(response._error)
        return response.text
    except Exception as e:
        return "❌ Exception: " + str(e)
            
#---------------------------------------------Message History-------------------------------------------------
def update_message_history(user_id, text):
    # Check if user_id already exists in the dictionary
    if user_id in message_history:
        # Append the new message to the user's message list
        message_history[user_id].append(text)
        # If there are more than 12 messages, remove the oldest one
        if len(message_history[user_id]) > MAX_HISTORY:
            message_history[user_id].pop(0)
    else:
        # If the user_id does not exist, create a new entry with the message
        message_history[user_id] = [text]
        
def get_formatted_message_history(user_id):
    """
    Function to return the message history for a given user_id with two line breaks between each message.
    """
    if user_id in message_history:
        # Join the messages with two line breaks
        return '\n\n'.join(message_history[user_id])
    else:
        return "No messages found for this user."
    
#---------------------------------------------Sending Messages-------------------------------------------------
async def split_and_send_messages(message_system, text, max_length):
    # Split the string into parts
    messages = []
    for i in range(0, len(text), max_length):
        sub_message = text[i:i+max_length]
        messages.append(sub_message)

    # Send each part as a separate message
    for string in messages:
        await message_system.channel.send(string)    

#cleans the discord message of any <@!123456789> tags
def clean_discord_message(input_string):
    # Create a regular expression pattern to match text between < and >
    bracket_pattern = re.compile(r'<[^>]+>')
    # Replace text between brackets with an empty string
    cleaned_content = bracket_pattern.sub('', input_string)
    return cleaned_content  

#---------------------------------------------Scraping Text from URL-------------------------------------------------

async def ProcessURL(message_str):
    pre_prompt = remove_url(message_str)
    if pre_prompt == "":
        pre_prompt = SUMMERIZE_PROMPT   
    if is_youtube_url(extract_url(message_str)):
        print("Processing Youtube Transcript")   
        return await generate_response_with_text(pre_prompt + " " + get_FromVideoID(get_video_id(extract_url(message_str))))     
    if extract_url(message_str):       
        print("Processing Standards Link")       
        return await generate_response_with_text(pre_prompt + " " + extract_text_from_url(extract_url(message_str)))
    else:
        return "No URL Found"
    
def extract_url(string):
    url_regex = re.compile(
        r'(?:(?:https?|ftp):\/\/)?'  # http:// or https:// or ftp://
        r'(?:\S+(?::\S*)?@)?'  # user and password
        r'(?:'
        r'(?!(?:10|127)(?:\.\d{1,3}){3})'
        r'(?!(?:169\.254|192\.168)(?:\.\d{1,3}){2})'
        r'(?!172\.(?:1[6-9]|2\d|3[0-1])(?:\.\d{1,3}){2})'
        r'(?:[1-9]\d?|1\d\d|2[01]\d|22[0-3])'
        r'(?:\.(?:1?\d{1,2}|2[0-4]\d|25[0-5])){2}'
        r'(?:\.(?:[1-9]\d?|1\d\d|2[0-4]\d|25[0-4]))'
        r'|'
        r'(?:www.)?'  # www.
        r'(?:[a-z\u00a1-\uffff0-9]-?)*[a-z\u00a1-\uffff0-9]+'
        r'(?:\.(?:[a-z\u00a1-\uffff]{2,}))+'
        r'(?:\.(?:[a-z\u00a1-\uffff]{2,})+)*'
        r')'
        r'(?::\d{2,5})?'  # port
        r'(?:[/?#]\S*)?',  # resource path
        re.IGNORECASE
    )
    match = re.search(url_regex, string)
    return match.group(0) if match else None

def remove_url(text):
  url_regex = re.compile(r"https?://\S+")
  return url_regex.sub("", text)

def extract_text_from_url(url):
    # Request the webpage content
    headers = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:120.0) Gecko/20100101 Firefox/120.0",
                   "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
                   "Accept-Language": "en-US,en;q=0.5"}
    try:
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            return "Failed to retrieve the webpage"

        # Parse the webpage content
        soup = BeautifulSoup(response.text, 'html.parser')

        # Extract text from  tags
        paragraphs = soup.find_all('p')
        text = ' '.join([paragraph.text for paragraph in paragraphs])

        # Clean and return the text
        return ' '.join(text.split())
    except Exception as e:
        print(f"Error scraping {url}: {str(e)}")
        return "" 
    
#---------------------------------------------Youtube API-------------------------------------------------

from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import TranscriptsDisabled
import urllib.parse as urlparse

def get_transcript_from_url(url):
    try:
        # parse the URL
        parsed_url = urlparse.urlparse(url)
        
        # extract the video ID from the 'v' query parameter
        video_id = urlparse.parse_qs(parsed_url.query)['v'][0]
        
        # get the transcript
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
        
        # concatenate the transcript
        transcript = ' '.join([i['text'] for i in transcript_list])
        
        return transcript
    except (KeyError, TranscriptsDisabled):
        return "Error retrieving transcript from YouTube URL"

def is_youtube_url(url):
    # Regular expression to match YouTube URL
    if url == None:
        return False
    youtube_regex = (
        r'(https?://)?(www\.)?'
        '(youtube|youtu|youtube-nocookie)\.(com|be)/'
        '(watch\?v=|embed/|v/|.+\?v=)?([^&=%\?]{11})'
    )

    youtube_regex_match = re.match(youtube_regex, url)
    return youtube_regex_match is not None  # return True if match, False otherwise


def get_video_id(url):
    # parse the URL
    parsed_url = urlparse.urlparse(url)
    
    if "youtube.com" in parsed_url.netloc:
        # extract the video ID from the 'v' query parameter
        video_id = urlparse.parse_qs(parsed_url.query).get('v')
        
        if video_id:
            return video_id[0]
        
    elif "youtu.be" in parsed_url.netloc:
        # extract the video ID from the path
        return parsed_url.path[1:] if parsed_url.path else None
    
    return "Unable to extract YouTube video and get text"

def get_FromVideoID(video_id):
    try:
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
        
        # concatenate the transcript
        transcript = ' '.join([i['text'] for i in transcript_list])
        
        return transcript
    except (KeyError, TranscriptsDisabled):
        return "Error retrieving transcript from YouTube URL"
    

#---------------------------------------------PDF and Text Processing Attachments-------------------------------------------------

async def ProcessAttachments(message,prompt):
    if prompt == "":
        prompt = SUMMERIZE_PROMPT  
    for attachment in message.attachments:
        await message.add_reaction('📄')
        async with aiohttp.ClientSession() as session:
            async with session.get(attachment.url) as resp:
                if resp.status != 200:
                    await message.channel.send('Unable to download the attachment.')
                    return
                if attachment.filename.lower().endswith('.pdf'):
                    print("Processing PDF")
                    try:
                        pdf_data = await resp.read()
                        response_text = await process_pdf(pdf_data,prompt)
                    except Exception as e:
                        await message.channel.send('❌ CANNOT PROCESS ATTACHMENT')
                        return
                else:
                    try:
                        text_data = await resp.text()
                        response_text = await generate_response_with_text(prompt+ ": " + text_data)
                    except Exception as e:
                        await message.channel.send('CANNOT PROCESS ATTACHMENT')
                        return

                await split_and_send_messages(message, response_text, 1700)
                return
            

async def process_pdf(pdf_data,prompt):
    pdf_document = fitz.open(stream=pdf_data, filetype="pdf")
    text = ""
    for page in pdf_document:
        text += page.get_text()
    pdf_document.close()
    print(text)
    return await generate_response_with_text(prompt+ ": " + text)

#---------------------------------------------Run Bot-------------------------------------------------
bot.run(DISCORD_BOT_TOKEN)
