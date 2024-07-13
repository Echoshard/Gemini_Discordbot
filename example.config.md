From GeminiDiscordBot.py
{
    "GOOGLE_AI_KEY": "",
    "DISCORD_BOT_TOKEN": "",
    "MAX_HISTORY": 0,
    "SUMMERIZE_PROMPT": "Give me 5 bullets about",
    "text_generation_config": {
        "temperature": 0.9,
        "top_p": 1,
        "top_k": 1,
        "max_output_tokens": 512
    },
    "safety_settings": [
        {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_ONLY_HIGH"},
        {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_ONLY_HIGH"},
        {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_ONLY_HIGH"},
        {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_ONLY_HIGH"}
    ],
    "model_name": "gemini-1.5-flash",
    "system_instruction":"" 
}


From GeminiSimple.py
{
    "GOOGLE_AI_KEY": "",
    "DISCORD_BOT_TOKEN": "",
    "MAX_HISTORY": 0,
    "SUMMERIZE_PROMPT": "Give me 5 bullets about", 
    "text_generation_config": {
        "temperature": 0.9,
        "top_p": 1,
        "top_k": 1,
        "max_output_tokens": 512
    },
    "image_generation_config" : {
        "temperature": 0.4,
        "top_p": 1,
        "top_k": 32,
        "max_output_tokens": 512
    },
    "safety_settings": [
        {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_ONLY_HIGH"},
        {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_ONLY_HIGH"},
        {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_ONLY_HIGH"},
        {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_ONLY_HIGH"}
    ],
    "model_name": "gemini-1.5-flash",
    "system_instruction":"You are a helpful bot!",
    "image_instruction": "You are a helpful bot!"
}