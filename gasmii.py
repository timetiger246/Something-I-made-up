import os
import google.generativeai as genai
from dotenv import load_dotenv


load_dotenv()

GOOGLE_AI_KEY = os.getenv("GOOGLE_AI_KEY")








genai.configure(api_key=GOOGLE_AI_KEY)
text_generation_config = {
    "temperature": 0.9,
    "top_p": 1,
    "top_k": 5, 
    "max_output_tokens": 8122,
}
videoMetadata = {
    "startOffset" : {
              "seconds": 60 ,
              "nanos": 60
    }
}
image_generation_config = {
    "temperature": 0.4,
    "top_p": 1,
    "top_k": 32,

    "max_output_tokens": 1024,
}
safety_settings = [
    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"}
]
text_model = genai.GenerativeModel(model_name="gemini-pro", generation_config=text_generation_config, safety_settings=safety_settings)

image_model = genai.GenerativeModel(model_name="gemini-pro-vision", generation_config=image_generation_config,safety_settings=safety_settings)


