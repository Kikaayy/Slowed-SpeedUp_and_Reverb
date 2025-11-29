from pydub import AudioSegment
import discord
from discord.ext import commands
from difflib import SequenceMatcher
import os
import uuid
import glob
import random
import subprocess
import yt_dlp
from dotenv import load_dotenv

def speed_change(input_file, speed=1.0):
    sound = AudioSegment.from_file(input_file)
    sound_with_altered_frame_rate = sound._spawn(sound.raw_data, overrides={
        "frame_rate": int(sound.frame_rate * speed)
    })

    return sound_with_altered_frame_rate.set_frame_rate(sound.frame_rate)

def apply_effects(input_file, output_file, speed=1, randome=""):
    sound = speed_change(input_file, speed)
    temp_path = f"temp/temp_{randome}.mp3"
    sound.export(temp_path, format="mp3")
    filter_complex = (
        "[0:a]asplit[a0][a1];"
        "[a1]aecho=0.8:0.9:60|75|90|105|115|120:0.4|0.3|0.25|0.15|0.10|0.05[ae];"
        "[a0][ae]amix=inputs=2:weights=1 1,volume=-3dB"
    )
    ffmpeg_cmd = [
        "ffmpeg", "-y",
        "-i", temp_path,
        "-filter_complex", filter_complex,
        output_file,
    ]
    subprocess.run(ffmpeg_cmd, check=True)

def get_song(song_title):
    song_title = song_title.replace("/", "")
    search_query = f"ytsearch1:{song_title}"  # Search for 1 result
    
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'extract_flat': True,
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            result = ydl.extract_info(search_query, download=False)
            if result and 'entries' in result and len(result['entries']) > 0:
                video = result['entries'][0]
                video_url = f"https://www.youtube.com/watch?v={video['id']}"
                # Clean title for filename
                title = video['title']
                for char in ['/', '\\', '.', ':', '|', '?', '!', '+', '"', "'", ' ']:
                    title = title.replace(char, '_')
                title = title.encode('ascii', 'ignore').decode('ascii')
                if not title:
                    title = "song"
                print(f"Found: {video['title']}")
                print(f"URL: {video_url}")
                return video_url, title
    except Exception as e:
        print(f"Search error: {e}")
    
    return None

def dlyt(url, output_path):
    # output_path should be "input/songname" 
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': output_path,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'quiet': False,
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
            print(f"Downloaded: {output_path}.mp3")
    except Exception as e:
        print(f"Download error: {e}") 

def get_video_name(url):
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            title = info.get('title', 'video')
            # Clean title for filename
            for char in ['/', '\\', '.', ':', '|', '?', '!', '+', '"', "'", ' ']:
                title = title.replace(char, '_')
            title = title.encode('ascii', 'ignore').decode('ascii')
            if not title:
                title = "video"
            return title
    except Exception as e:
        print(f"Error getting video name: {e}")
        return None

def main(file, choice="slow"):
    in_path = file
    if os.path.exists(file):
        in_path = file
    elif os.path.exists(os.path.join("input", file)):
        in_path = os.path.join("input", file)
    else:
        print("File not found")
        exit(1)

    if choice=="s" or choice=="slow":
        speed=0.86
        choice="slowed"
    elif choice=="f" or choice=="fast":
        speed=1.15
        choice="sped-up"
    else:
        print("Invalid choice")
        exit()
        
    file_name = os.path.splitext(os.path.basename(in_path))[0]
    randome=str(uuid.uuid4())
    os.makedirs("output", exist_ok=True)
    os.makedirs("temp", exist_ok=True)
    apply_effects(in_path, f"output/{file_name}_{choice}.mp3", speed, randome)
    os.remove(f"temp/temp_{randome}.mp3")
    return f"output/{file_name}_{choice}.mp3"

def dowl(message):
    return

if __name__ == "__main__":
    load_dotenv()
    DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
    if not DISCORD_TOKEN:
        raise RuntimeError("Missing DISCORD_TOKEN, create a .env file with DISCORD_TOKEN=<your_token>.")
    intents = discord.Intents.default()
    intents.messages = True

    bot = commands.Bot(command_prefix='', intents=intents)

    @bot.event
    async def on_message(message):
        if message.author.bot==True:
            return 
        else:
            channel = message.channel
            message_id = message.id  
            choice = 'c'
            name=""
            fetched_message = await channel.fetch_message(message_id)
            content = fetched_message.content
            if content[0]=="/":
                randomm = random.randint(0, 100000)
                if randomm==6969:
                    await channel.send("GAY")
                return
            if content.count("youtube.com")==0 and content.count("youtu.be")==0:
                if content.count(".mp3")==0 and content.count(".flac")==0:
                    choice=(content[-1] if content[-1] in ['s','f'] else 's')
                    content, name=get_song(content)
                else:
                    choice=(content[-1] if content[-1] in ['s','f'] else 's')
                    content=content.split('.mp3' if '.mp3' in content else '.flac')[0]+('.mp3' if '.mp3' in content else '.flac')
            if content.count("youtube.com")!=0 or content.count("youtu.be")!=0:
                if choice=='c': 
                    choice=(content[-1] if content[-1] in ['s','f'] else 's')
                cc=content.split(" ")
                cc=get_video_name(cc[0])
                if cc==None:
                    await channel.send("Vidéo non trouvée") 
                    return
                await channel.send(f"Téléchargment de **{cc}** version {'sped-up + reverb' if choice=='f' else 'slowed + reverb'}")
                print(f"Téléchargment de {content}")
                if name=="":
                    name=cc
                dlyt(content, "input/"+name) 
                content=f"{name}.mp3"
            print(f"{content} en mode {'sped-up + reverb' if choice=='f' else 'slowed + reverb'}")
            if "input/"+content not in glob.glob("input/*"):
                await channel.send(f"File not found")
                return
            #ADD OK REACTION TO MESSAGE
            await channel.send(f"Création de la magie sur {content} en mode {'sped-up + reverb' if choice=='f' else 'slowed + reverb'} en cours...")
            main(content,choice)
            outputtt=f"output/{os.path.splitext(content)[0]}_{'sped-up' if choice=='f' else 'slowed'}.mp3"
            print(f"sending file {outputtt}")
            #REMOVE OK REACTION TO MESSAGE
            #ADD SENDING REACTION TO MESSAGE
            await channel.send(file=discord.File(outputtt))
            #REMOVE MESSAGE
            print("file sent")
            os.remove(f"input/{content}")
            os.remove(f"output/{os.path.splitext(content)[0]}_{'sped-up' if choice=='f' else 'slowed'}.mp3")

    bot.run(DISCORD_TOKEN)
