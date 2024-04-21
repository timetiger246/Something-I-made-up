import aiohttp
import asyncio
import discord
import io
import json
import os
import random
import threading
import urllib
from discord.ext import commands
from dotenv import load_dotenv
from discord.ext import commands
from discord import Embed, app_commands
from discord.ext import commands
from gasmii import text_model, image_model
from discord import ui
from definitions import *
import requests
from datetime import datetime
from dotenv import load_dotenv
import datetime
from bs4 import BeautifulSoup

message_history = {}
intents = discord.Intents.all()
bot = commands.Bot(command_prefix="/", intents=intents, heartbeat_timeout=60)

load_dotenv()


DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN") # env option bah t7oti token te3 bot t3k w tconnectih lel code 
MAX_HISTORY = int(os.getenv("MAX_HISTORY")) 



@bot.event
async def on_ready():
    await bot.tree.sync()
    num_commands = len(bot.commands)
    
    invite_link = discord.utils.oauth_url(
        bot.user.id,
        permissions=discord.Permissions(),
        scopes=("bot", "applications.commands")
    )

    def print_in_color(text, color):
        return f"\033[{color}m{text}\033[0m"

    if os.name == 'posix':
        os.system('clear')
    elif os.name == 'nt':
        os.system('cls')

    ascii_art = """
    \033[1;35m
    
███████╗██████╗ ███████╗██╗  ██╗████████╗██████╗ ██╗   ██╗███╗   ███╗
██╔════╝██╔══██╗██╔════╝██║ ██╔╝╚══██╔══╝██╔══██╗██║   ██║████╗ ████║
███████╗██████╔╝█████╗  █████╔╝    ██║   ██████╔╝██║   ██║██╔████╔██║
╚════██║██╔═══╝ ██╔══╝  ██╔═██╗    ██║   ██╔══██╗██║   ██║██║╚██╔╝██║
███████║██║     ███████╗██║  ██╗   ██║   ██║  ██║╚██████╔╝██║ ╚═╝ ██║
╚══════╝╚═╝     ╚══════╝╚═╝  ╚═╝   ╚═╝   ╚═╝  ╚═╝ ╚═════╝ ╚═╝     ╚═╝
                                                                     
\033[0m
    """

    print(ascii_art)
    print(print_in_color(f"{bot.user} aka {bot.user.name} has connected to Discord!", "\033[1;97"))
    print(print_in_color(f"  Loaded {num_commands} commands", "1;35"))
    print(print_in_color(f"      Invite link: {invite_link}", "1;36"))











class RegenerateButton(ui.Button):
    def __init__(self, author_id, prompt):
        super().__init__(label=" Regenerate", style=discord.ButtonStyle.blurple, custom_id=f"regenerate_button_{author_id}_{prompt}")
        
        self.emoji = "🔄"  
    async def callback(self, interaction: discord.Interaction):
        
        author_id_from_button = int(self.custom_id.split("_")[2])
        prompt_from_button = self.custom_id.split("_")[3]

        if interaction.user.id == author_id_from_button:
            response_text = await generate_response_with_text(prompt_from_button, interaction.message) 


            
            await interaction.message.edit(view=None)

            
            new_view = ui.View()
            new_view.add_item(RegeneratedButton())
            new_view.add_item(ResetButton(author_id_from_button))
            new_view.add_item(RegenerateButton(author_id_from_button, prompt_from_button))  
            new_view.add_item(EditButton(author_id_from_button))
            new_view.add_item(DeleteMessageButton(author_id_from_button))

            
            
            await split_and_send_messages(interaction.message, response_text, 1700, view=new_view)  
        else:
            await interaction.response.send_message("Only the original user can regenerate the response.", ephemeral=True)

           








            
class ResetButton(ui.Button):
    def __init__(self, author_id):
        super().__init__(label="Reset", style=discord.ButtonStyle.red, custom_id=f"reset_button_{author_id}")
        self.emoji = "♻️"

    async def callback(self, interaction: discord.Interaction):
        
        author_id_from_button = int(self.custom_id.split("_")[2])

        if interaction.user.id == author_id_from_button:
            if author_id_from_button in message_history:
                del message_history[author_id_from_button]
            await interaction.response.send_message("History Reset for user: " + str(interaction.user.name), ephemeral=True)
        else:
            await interaction.response.send_message("Only the original user can reset their history.", ephemeral=True)


class DeleteMessageButton(ui.Button):
    def __init__(self, author_id):
        super().__init__(label="Delete Message", style=discord.ButtonStyle.red, emoji="❌")
        self.author_id = author_id

    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.author_id:
            await interaction.response.send_message("Only the original user can delete the message.", ephemeral=True)
            return

        try:
            await interaction.message.delete()
            await interaction.response.send_message("Message deleted!", ephemeral=True)
        except discord.DiscordException as e:
            await interaction.response.send_message(f"An error occurred: {e}", ephemeral=True)




# Define the Regenerated button (disabled)
class RegeneratedButton(ui.Button):
    def __init__(self):
        super().__init__(label="Regenerated", style=discord.ButtonStyle.gray, disabled=True)
        
class ClearPersonaButton(ui.Button):
    def __init__(self, author_id):
        super().__init__(label="Clear Persona", style=discord.ButtonStyle.red, emoji="", custom_id=f"clear_button_{author_id}")
        self.user_id = author_id
        self.emoji = "🧹"

    async def callback(self, interaction: discord.Interaction):
        author_id_from_button = int(self.custom_id.split("_")[2])

        if interaction.user.id == author_id_from_button:
            try:
                with open("personas.json", "r") as f:
                    personas = json.load(f)
                personas.pop(str(self.user_id))  
                with open("personas.json", "w") as f:
                    json.dump(personas, f)

                await interaction.response.send_message(
                    "Your custom persona has been cleared. I'll now use the default persona.",
                    ephemeral=True
                )
            except Exception as e:
                await interaction.response.send_message(
                    f"An error occurred while clearing your persona: {e}", ephemeral=True
                )
        else:
            await interaction.response.send_message("Only the original user can clear the persona.", ephemeral=True)


class EditButton(ui.Button):
    def __init__(self, author_id):
        super().__init__(label="Edit bot's persona", style=discord.ButtonStyle.green, custom_id=f"edit_button_{author_id}")
        self.emoji = "✏️"  

    async def callback(self, interaction: discord.Interaction):
        author_id_from_button = int(self.custom_id.split("_")[2])

        if interaction.user.id == author_id_from_button:
            try:
                persona_text = await retrieve_persona_text(interaction.user.id)
                modal = EditPersonaModal(persona_text)
                await interaction.response.send_modal(modal)
            except Exception as e:
                await interaction.response.send_message(f"An error occurred: {e}")
        else:
            await interaction.response.send_message("Only the original user can edit the persona.", ephemeral=True)


class EditPersonaModal(ui.Modal):
    def __init__(self, current_persona):
        super().__init__(title="Edit Persona")
        self.persona_input = ui.TextInput(
            label="You are a...",  
            style=discord.TextStyle.long
        )
        self.add_item(self.persona_input)

        async def on_ready(self):
            self.persona_input.value = current_persona  

    async def on_submit(self, interaction: discord.Interaction):
        new_persona_text = self.persona_input.value
        await save_persona_text(interaction.user.id, new_persona_text)  
        await interaction.response.send_message(f"Persona updated successfully!", ephemeral=True)





@bot.hybrid_command(name="reset", description="Clears bot message history")

async def reset(ctx):
    
    global message_history
    message_history = {}
    await ctx.send("🤖 Bot message history has been cleared.")




@bot.hybrid_command(name="show_chatbot_channels", description="Displays the channels where the chatbot is currently enabled.")
async def show_chatbot_channels(ctx):
    enabled_channels = get_enabled_channels_in_guild(ctx.guild.id)  # Retrieve enabled channels for the server

    if not enabled_channels:
        await ctx.send("The chatbot is not currently enabled in any channels on this server.")
        return

    embed = discord.Embed(
        title="Chatbot Enabled Channels",
        color=discord.Color.blue(),
    )
    for channel in enabled_channels:
        embed.add_field(
            name=channel.mention,
            value=f"ID: {channel.id}",
            inline=False,  # Display each channel on a separate line
        )

    embed.set_footer(text=f"Requested by {ctx.author.display_name}")  


    await ctx.send(embed=embed)


@bot.hybrid_command(name="toggle_chatbot", description="Toggles the chatbot on or off in a specific channel")
async def toggle_chatbot(ctx, channel: discord.TextChannel = None):

    if channel is None:
        channel = ctx.channel

    if is_channel_enabled(channel.id):  # Check if the channel is already enabled
        # Disable the chatbot in the current channel
        toggle_enabled_channel(channel.id)  # Remove from enabled channels
        await ctx.send("Chatbot disabled in this channel.")
    else:
        # Enable the chatbot in the specified channel
        toggle_enabled_channel(channel.id)  # Add to enabled channels
        await ctx.send(f"Chatbot enabled in {channel.mention}.")

    # Always save changes, regardless of whether enabling or disabling
    save_enabled_channels()  # Save changes to JSON file



########################################################################MESSAGE HANDLER####################################################################################




# Event handler for new messages
@bot.event
async def on_message(message):

    if message.author == bot.user or message.mention_everyone:
        return
    
    # Check if the channel is enabled or if the bot is mentioned
    if (
        message.channel.id in enabled_channels  # Check using the loaded channel IDs
        or bot.user.mentioned_in(message)
        or isinstance(message.channel, discord.DMChannel)
    ):

        cleaned_text = clean_discord_message(message.content)
        
        async with message.channel.typing():

                
                

                # Check for image attachments
                if message.attachments:
                    print("New Image Message FROM:" + str(message.author.id) + ": " + cleaned_text)
                    #Currently no chat history for images
                    for attachment in message.attachments:
                        #these are the only image extentions it currently accepts
                        if any(attachment.filename.lower().endswith(ext) for ext in ['.png', '.jpg', '.jpeg', '.gif', '.webp']):
                            await message.add_reaction('🖼️')

                            async with aiohttp.ClientSession() as session:
                                async with session.get(attachment.url) as resp:
                                    if resp.status != 200:
                                        await message.channel.send('Unable to download the image.')
                                        return
                                    image_data = await resp.read()
                                    response_text = await generate_response_with_image_and_text(image_data, cleaned_text)
                                    update_message_history(message.author.id, cleaned_text)  # Store prompt for regeneration

                                    
                                    view = ui.View()
                                    view.add_item(ResetButton(message.author.id))
                                    view.add_item(RegenerateButton(message.author.id, cleaned_text))
                                    view.add_item(DeleteMessageButton(message.author.id))
                                    
                                    await split_and_send_messages(message, response_text, 2000, view=view, only_last_part=True)
                                    


                                    return    
                #Not an Image do text response
                else:
                    print("New Message FROM:" + str(message.author.id) + ": " + cleaned_text)
                    await message.add_reaction('💨')

                    

                    
                    if cleaned_text not in message_history.get(message.author.id, []):
                        update_message_history(message.author.id, cleaned_text)

                    
                    response_text = await generate_response_with_text(get_formatted_message_history(message.author.id), message)

                    
                    if response_text not in message_history.get(message.author.id, []):
                        update_message_history(message.author.id, response_text)

                    
                    view = ui.View()
                    view.add_item(ResetButton(message.author.id))
                    view.add_item(RegenerateButton(message.author.id, cleaned_text))
                    view.add_item(EditButton(message.author.id))  
                    view.add_item(DeleteMessageButton(message.author.id))
                    
                    await split_and_send_messages(message, response_text, 2000, only_last_part=True, view=view)


                    
                    

                
                # Check for file attachments and process supported formats
                if message.attachments:
                    view = None  
                    for attachment in message.attachments:
                        file_extension = attachment.filename.split('.')[-1].lower()
                        if file_extension in ['txt', 'rtf', 'md', 'html', 'xml', 'csv', 'json', 'js', 'css', 'py', 'java', 'c', 'cpp',
                                            'php', 'rb', 'swift', 'sql', 'sh', 'bat', 'ps1', 'ini', 'cfg', 'conf', 'log', 'svg',
                                            'epub', 'mobi', 'tex', 'docx', 'odt', 'xlsx', 'ods', 'pptx', 'odp', 'eml', 'htaccess',
                                            'nginx.conf', 'pdf', 'yml', 'env']:
                            await message.add_reaction('📙')
                            file_type = attachment.filename
                            file_content = await attachment.read()

                            try:
                                if file_extension in ['txt', 'rtf', 'md', 'html', 'xml', 'csv', 'json', 'js', 'css', 'py', 'java', 'c', 'cpp',
                                                    'php', 'rb', 'swift', 'sql', 'sh', 'bat', 'ps1', 'ini', 'cfg', 'conf', 'log', 'svg',
                                                    'epub', 'mobi', 'tex', 'odt', 'xlsx', 'ods', 'pptx', 'odp', 'eml', 'htaccess',
                                                    'nginx.conf', 'yml', 'env']:
                                    text_content = file_content.decode('utf-8')  
                                elif file_extension == 'pdf':
                                    pdf_reader = PyPDF2.PdfReader(io.BytesIO(file_content))
                                    num_pages = len(pdf_reader.pages)
                                    text_content = ""
                                    for page_num in range(num_pages):
                                        page = pdf_reader.pages[page_num]
                                        text_content += page.extract_text()
                                elif file_extension == 'docx':
                                    doc = docx.Document(io.BytesIO(file_content))
                                    text_content = "\n".join([paragraph.text for paragraph in doc.paragraphs])

                               
                                response_text = await generate_response_with_text(text_content, message)  

                                update_message_history(message.author.id, text_content)  


                                
                                if not view:  
                                    view = ui.View()
                                    view.add_item(ResetButton(message.author.id))
                                    view.add_item(RegenerateButton(message.author.id, cleaned_text))
                                    view.add_item(DeleteMessageButton(message.author.id))
                                    view.add_item(EditButton(message.author.id)) 
                                    
                                
                                await split_and_send_messages(message, response_text, 2000, view=view)

                            except Exception as e:
                                await message.channel.send(f"Error processing file: {e}")

                









@bot.hybrid_command(name="custom_persona", description="Sets a custom persona for the bot's responses")
async def custom_persona(ctx, persona_text: str):
    try:
        with open("personas.json", "r") as f:
            personas = json.load(f)
    except FileNotFoundError:
        personas = {}  
    except json.JSONDecodeError:
        print("Error loading personas: Invalid JSON format in personas.json")
        return await ctx.send("Error loading personas. Please try again later.")

    personas[str(ctx.author.id)] = persona_text

    with open("personas.json", "w") as f:
        json.dump(personas, f, indent=4)

    await ctx.send(f"Your custom persona has been set! I'll now respond based on your unique personality.")



@bot.hybrid_command(name="bot_persona", description="Shows your setuped custom persona text")
async def bpt_personal(ctx):
    author_id = ctx.author.id
    persona_text = load_persona_from_json(author_id)

    view = discord.ui.View()

    if persona_text:
        view.add_item(EditButton(author_id))
        view.add_item(ClearPersonaButton(author_id)) 

        embed = discord.Embed(title="Your Bot Persona", description=persona_text, color=discord.Color.blue())
        await ctx.send(embed=embed, view=view)
    else:
        embed = discord.Embed(title="Bot Persona Not Set", description="You haven't set a custom persona yet. Use the `/custom_persona` command to create one!", color=discord.Color.orange())
        await ctx.send(embed=embed)




#----------------------------------------------------------------gen text--------------------------------#






from datetime import datetime         




async def gather_additional_info(message):
    """Collects contextual information about the user and server."""

    try:
        author_name = message.author.name
        author_id = message.author.id
        user_roles = ", ".join([role.name for role in message.author.roles])
        user_activity = message.author.activity
        current_time = datetime.now().strftime("%H:%M")

        if message.guild:  # Server context
            server_name = message.guild.name
            channel_name = message.channel.name
            user_nicknames = ", ".join([member.nick for member in message.guild.members if member.nick])
            server_icon = message.guild.icon
            server_banner = message.guild.banner
            server_creation_date = message.guild.created_at.strftime("%B %d, %Y")
            voice_channel_status = "Active" if message.guild.voice_channels and any(
                member.voice for member in message.guild.members
            ) else "Inactive"
            member_count = message.guild.member_count
            try:
                server_region = message.guild.voice_channels[0].rtc_region
            except IndexError:
                server_region = "Unknown"
        else:  # DM context
            server_name = "Direct Messages"
            channel_name = "Direct Messages"
            user_nicknames = "N/A"
            server_icon = "N/A"
            server_banner = "N/A"
            server_creation_date = "N/A"
            voice_channel_status = "N/A"
            member_count = "N/A"
            server_region = "N/A"

        return {
            "*The user who is talking to you his name is": author_name,
            "The user who is talking to you his id is = author_id": author_id,
            "User_roles = author roles = the user who is talking to you roles": user_roles,
            "The activity of author = user_activity = the activity of the user who's talking to you ": user_activity,
            "current_time": current_time,
            "Discord Server = server = the place where are you at = the place where are you talking is": server_name,
            "discord_server_channel_name": channel_name,
            "user_nicknames": user_nicknames,
            "server_icon": server_icon,
            "server_banner": server_banner,
            "server_creation_date": server_creation_date,
            "voice_channel_status": voice_channel_status,
            "server_member_count": member_count,
            "server_region": server_region,
        }
    except Exception as e:
        print(f"Error gathering additional info: {e}")
        return {}


async def generate_response_with_text(message_text, message):
    try:
        with open("personas.json", "r") as f:
            personas = json.load(f)

        character_prompt = personas.get(str(message.author.id), default_persona)


        additional_info = await gather_additional_info(message)

        

        
        # Construct prompt with enhanced persona integration:
        prompt_text = f"""
User message : {message_text}
* Chat Platform: Discord
{additional_info} \n\n\n\n\n\n

You are {character_prompt}. Act like that and respond naturally and creatively, embodying this persona without explicitly revealing it.

"""     
        
        # URL Detection and Web Scraping:
        urls = re.findall(r'(https?://\S+)', message_text)  # Find all URLs
        for url in urls:
            print(f"\033[1;32mScraping the website '\033[1;33m{url}\033[1;32m'\033[0m")
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status == 200:  # Check for successful response
                        html_content = await response.text()
                        soup = BeautifulSoup(html_content, "html.parser")

                        # Extract main content (adjust selectors as needed):
                        main_content_tags = [
                            "p", "a", "article", "div.main-content", "main"
                        ]
                        main_content_text = ""
                        for tag in main_content_tags:
                            main_content_text += soup.get_text(tag) + " "

                        title_meta_tag = soup.find("title")
                        title = title_meta_tag.get_text(strip=True) if title_meta_tag else "No title found"

                        # Extract additional relevant information:
                        
                        key_points = soup.find_all("h2, h3")  # Example using headings
                        key_points_text = [kp.text.strip() for kp in key_points]

                        prompt_text += (
                            f"\n**Title:** {title}\n"
                            f"**Main Content:** {main_content_text[:2000]}\n"
                            
                            f"**Key Points:** {', '.join(key_points_text)}"
                        )
                    else:
                        print(f"Error fetching URL: {url}, status code: {response.status}")
                        prompt_text += f"\n**Error fetching website:** {url}"    
        prompt_parts = [prompt_text]
        
        print("Got textPrompt: " + prompt_text)
        response = text_model.generate_content(prompt_parts)

        if response._error:
            return "❌" + str(response._error)

        

        return response.text

    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading personas: {e}")
        return "Sorry, I'm having trouble accessing my personality data. Please try again later."







async def generate_response_with_image_and_text(image_data, text):
    image_parts = [{"mime_type": "image/jpeg", "data": image_data}]
    prompt_parts = [image_parts[0], f"\n{text if text else 'What is this a picture of?'}"]
    response = image_model.generate_content(prompt_parts)

    try:
        return response.text  # Attempt to access text
    except IndexError:
        print("Image model generated no text response.")  # Informative error message
        # Consider alternative actions here, e.g., prompting for more info or suggesting different prompts
        return "I'm unable to generate a text response based on the image and text you provided. Could you please rephrase your request or provide more context?"

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




async def split_and_send_messages(message, text, max_length, view=None, only_last_part=True):
    """Splits a long text into multiple messages and sends them individually.

    Args:
        message (discord.Message): The original message to reply to.
        text (str): The long text to split and send.
        max_length (int): The maximum length of each message part.
        view (discord.ui.View, optional): A view to attach to the last message part. Defaults to None.
        only_last_part (bool, optional): Whether to mention the user only in the last message part. Defaults to True.
    """

    messages = []
    for i in range(0, len(text), max_length):
        sub_message = text[i:i+max_length]
        messages.append(sub_message)

   
    if view:
        for item in view.children:
            item.custom_id = item.custom_id[:100]  

    
    sent_messages = []  
    for i, chunk in enumerate(messages):
        if i == len(messages) - 1 or not only_last_part:  
            sent_message = await message.reply(f"{chunk}", suppress_embeds=True)
        else:
            sent_message = await message.reply(chunk, suppress_embeds=True)
        sent_messages.append(sent_message) 

   
    if i == len(messages) - 1 and view:
        last_bot_message = sent_messages[-1]  
        await last_bot_message.edit(view=view)  









# Function to clean Discord messages
def clean_discord_message(input_string):
    bracket_pattern = re.compile(r'<[^>]+>')
    cleaned_content = bracket_pattern.sub('', input_string)
    return cleaned_content




#---------------------------------------------Run Bot-------------------------------------------------
bot.run(DISCORD_BOT_TOKEN)
