import telegram
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from pydub import AudioSegment
import numpy as np
import timecode


def generate_timecode(fps, start, length):
    sample_rate = 44100
    duration = 1000 * length / fps
    t = np.linspace(start, start + length, int(sample_rate * length), endpoint=False)
    timecode = (np.sin(2 * np.pi * t * fps) + 1) * 128
    timecode = timecode.astype(np.uint8)
    timecode_audio = AudioSegment(
        timecode.tobytes(), 
        frame_rate=sample_rate,
        sample_width=1,
        channels=1
    )
    return timecode_audio


def start(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="Welcome! Send me the command /generate to generate a SMPTE Timecode WAV file.")


def generate(update, context):
    try:
        timecode_str = context.args[0]
        hours, minutes, seconds, frames = map(int, timecode_str.split(":"))
    except (IndexError, ValueError):
        context.bot.send_message(chat_id=update.effective_chat.id, text="Invalid start time. Please specify a start time in the format of `HH:MM:SS:FF`.")
        return
    
    fps = 24
    start = 3600 * hours + 60 * minutes + seconds + frames / fps
    length = 30  # seconds
    timecode_audio = generate_timecode(fps, start, length)
    timecode_audio.export("timecode.wav", format="wav")
    with open("timecode.wav", "rb") as f:
        context.bot.send_audio(chat_id=update.effective_chat.id, audio=f)
    context.bot.send_message(chat_id=update.effective_chat.id, text="SMPTE Timecode WAV file sent.")


def main():
    token = "6057333938:AAHD8Fr5_EdDL7OgSTQj6FrCKJrrLOVyWys"
    updater = Updater(token, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("generate", generate))
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
