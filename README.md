# SlowedReverb Discord Bot

This Python Discord bot allows you to ask for slowed + reverb or sped up + reverb versions of any song. Simply send the bot a message with the song's name or a YouTube link, and it will respond with the audio file that has been processed.

## Features
- Download songs from YouTube
- Apply slowed + reverb or sped up + reverb effects automatically
- Sends the audio file back in the Discord channel

## How to Use
In any channel, send a message with:
  - A YouTube link, or
  - The name of a song (the bot will search YouTube)
  - Optionally, add `s` (slowed) or `f` (sped up) at the end of your message to choose the effect (default is slowed)
3. The bot will reply with the processed audio file

### Example
```
lofi hip hop s
```
or
```
https://www.youtube.com/watch?v=dQw4w9WgXcQ f
```

## Setup
Don't forget to create a `.env` file with your Discord bot token:
  ```
  DISCORD_TOKEN="your_token_here"
  ```
