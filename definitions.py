
from datetime import datetime
import re


import random

from urllib.parse import quote
import aiohttp
import asyncio
import discord


from youtube_transcript_api import YouTubeTranscriptApi
import io
import json
import os
import random
import re
import threading
import urllib
from discord.ext import commands
from dotenv import load_dotenv
import re
from discord.ext import commands
from discord import Embed, app_commands
from discord.ext import commands
from gasmii import text_model, image_model
from discord import ui
from youtube_transcript_api import YouTubeTranscriptApi
import requests
import discord
import google.generativeai as genai
from datetime import datetime
from bs4 import BeautifulSoup
import datetime
from dotenv import load_dotenv
import time

message_history = {}
intents = discord.Intents.all()
bot = commands.Bot(command_prefix="/", intents=intents, heartbeat_timeout=60)








#ry----------------------------generate_response_with_text---------------------



def get_enabled_channels_in_guild(guild_id):
    with open("chatbot_channels.json", "r") as f:
        enabled_channels_data = json.load(f)

    enabled_channels = []
    for channel_id in enabled_channels_data:
        try:
            channel = bot.get_channel(int(channel_id))  # Get channel object from ID
            if channel.guild.id == guild_id:
                enabled_channels.append(channel)
        except discord.NotFound:
            # Channel no longer exists, remove from the JSON file
            enabled_channels_data.remove(channel_id)
            with open("chatbot_channels.json", "w") as f:
                json.dump(enabled_channels_data, f)

    return enabled_channels


# File path to store enabled channel IDs
channel_data_file = "chatbot_channels.json"

# Load enabled channel IDs from file, creating it if necessary
enabled_channels = set()  # Initialize as an empty set

try:
    with open(channel_data_file, "r") as f:
        enabled_channels = set(json.load(f))  # Load IDs into a set
except FileNotFoundError:
    pass  # No need to create an empty file

# Check if a channel is already enabled
def is_channel_enabled(channel_id):
    return channel_id in enabled_channels

# Add or remove a channel from the enabled list
def toggle_enabled_channel(channel_id):
  if channel_id in enabled_channels:
    enabled_channels.discard(channel_id)  # Remove channel ID
  else:
    enabled_channels.add(channel_id)  # Add channel ID


# Function to save enabled channel IDs to the JSON file
def save_enabled_channels():
    with open(channel_data_file, "w") as f:
        json.dump(list(enabled_channels), f)  # Convert set to list for JSON



def load_persona_from_json(user_id):
    try:
        with open("personas.json", "r") as f:
            personas = json.load(f)
            return personas.get(str(user_id), None)  # Return persona text or None if not found
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading personas: {e}")
        return None


def read_default_persona_from_file():
    try:
        with open("default_persona.txt", "r") as f:  
            default_persona = f.read()
            return default_persona
    except FileNotFoundError:
        print("Error: default_persona.txt file not found. Using default prompt.")
        return "You will act like a friendly and helpful assistant named Bard, ready to chat about any topic."
default_persona = read_default_persona_from_file() 


async def save_persona_text(user_id, persona_text):
    """Saves the persona text to the JSON file, limiting its length."""
    # Limit the persona text to 195 characters (or your preferred limit)
    

    with open("personas.json", "r") as f:
        personas = json.load(f)
    personas[str(user_id)] = persona_text
    with open("personas.json", "w") as f:
        json.dump(personas, f, indent=4)

async def retrieve_persona_text(user_id):
    """Retrieves the persona text for a user from the JSON file."""
    try:
        with open("personas.json", "r") as f:
            personas = json.load(f)
            return personas.get(str(user_id), None)  # Return persona text or None if not found
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading personas: {e}")
        return None












#from bs4 import BeautifulSoup

#def extract_best_results(response_text):
    #soup = BeautifulSoup(response_text, 'html.parser')
    #results = soup.find_all('div', class_='result')  # Adjust selector as needed
    #best_results = []
    #for result in results[:2]:  # Extract top 3 results
        #link = result.find('a')['href']
        #title = result.find('h3').text
        #snippet = result.find('span', class_='st').text  # Adjust selector as needed
        #best_results.append({'link': link, 'title': title, 'snippet': snippet})
    #return best_results


#async def search(prompt, internet_access):
    #async with aiohttp.ClientSession() as session:
        #try:
            #async with session.get(f"https://www.google.com/search?q={prompt.replace(' ', '+')}", headers={'User-Agent': 'Mozilla/5.0'}) as response:
                #response.raise_for_status()  # Raise an exception for non-200 status codes
                #best_results = extract_best_results(await response.text())  # Await the text content
                #return format_search_results(best_results)
        #except aiohttp.ClientError as e:
            #return f"Error fetching search results: {e}"
        




    