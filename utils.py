from logger import logging
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters, CallbackContext, \
    ConversationHandler
from transformers import pipeline
from database import set_up_connection
from googletrans import Translator
import os
import speech_recognition as sr
import requests
from pydub import AudioSegment

database, colletion_name = set_up_connection()


async def languages_available(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    This function displays all the languages available
    """
    l1 = ['afrikaans', 'albanian', 'amharic', 'arabic', 'armenian', 'azerbaijani', 'basque', 'belarusian', 'bengali',
          'bosnian', 'bulgarian', 'catalan', 'cebuano', 'chichewa', 'chinese (simplified)', 'chinese (traditional)',
          'corsican', 'croatian', 'czech', 'danish', 'dutch', 'english', 'esperanto', 'estonian', 'filipino', 'finnish',
          'french', 'frisian', 'galician', 'georgian', 'german', 'greek', 'gujarati', 'haitian creole', 'hausa',
          'hawaiian', 'hebrew', 'hebrew', 'hindi', 'hmong', 'hungarian', 'icelandic', 'igbo', 'indonesian', 'irish',
          'italian', 'japanese', 'javanese', 'kannada', 'kazakh', 'khmer', 'korean', 'kurdish (kurmanji)', 'kyrgyz',
          'lao', 'latin', 'latvian', 'lithuanian', 'luxembourgish', 'macedonian', 'malagasy', 'malay', 'malayalam',
          'maltese', 'maori', 'marathi', 'mongolian', 'myanmar (burmese)', 'nepali', 'norwegian', 'odia', 'pashto',
          'persian', 'polish', 'portuguese', 'punjabi', 'romanian', 'russian', 'samoan', 'scots gaelic', 'serbian',
          'sesotho', 'shona', 'sindhi', 'sinhala', 'slovak', 'slovenian', 'somali', 'spanish', 'sundanese', 'swahili',
          'swedish', 'tajik', 'tamil', 'telugu', 'thai', 'turkish', 'ukrainian', 'urdu', 'uyghur', 'uzbek',
          'vietnamese', 'welsh', 'xhosa', 'yiddish', 'yoruba', 'zulu']
    await context.bot.send_message(chat_id=update.effective_chat.id, text=l1)


# message
async def reply_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    This function is to analyze the text in the group
    """
    author = update.message.from_user.first_name
    try:
        logging.info(f'Text by user {author}, text is {update.message.text}')
        # Check if the user exists in the database, if not add the user
        user_data = database[colletion_name].find_one(
            {"user_id": update.message.from_user.id})
        if not user_data:
            user_data = {"user_id": update.message.from_user.id, "user_name": author, "warnings": 0}
            database[colletion_name].insert_one(user_data)

        warnings = user_data["warnings"]

        # code for handling links and abusive words...
        if len(update.message.entities):
            for entity in update.message.entities:
                if entity['type'] == 'url':
                    logging.info(f"{author} has send a link {update.message.text}")
                    reply = "This is warning {}.  {} Sending links are not allowed".format(
                        warnings, author)
                    if warnings > 2:
                        await context.bot.delete_message(
                            chat_id=update.effective_chat.id,
                            message_id=update.message.message_id)
                        await context.bot.send_message(chat_id=update.effective_chat.id,
                                                       text="You violated our rules")
                        try:
                            await context.bot.ban_chat_member(
                                chat_id=update.effective_chat.id,
                                user_id=update.message.from_user.id)
                            logging.info(f"Removed {author}")
                        except Exception as e:
                            logging.error(f'Error removing {author}', exc_info=context.error)
                    else:
                        warnings += 1
                        await context.bot.delete_message(
                            chat_id=update.effective_chat.id,
                            message_id=update.message.message_id)
                        await context.bot.send_message(chat_id=update.effective_chat.id,
                                                       text=reply)
        else:
            # Translating the text
            translator = Translator()
            text_to_translate = update.message.text
            detected_language = translator.detect(text_to_translate).lang

            target_language = 'hi'
            if detected_language != 'en':
                translated_text = translator.translate(text_to_translate, dest=target_language)
                logging.info(f"Original Text: {text_to_translate} (Detected Language: {detected_language})")
                logging.info(f"Translation to {target_language}: {translated_text.text}")
                # Use a pipeline as a high-level helper
                # Converting hindi translated text to english for its checking via transformer
                pipe = pipeline("translation", model="Helsinki-NLP/opus-mt-hi-en")
                logging.info(pipe(translated_text.text))

                # Passing translated english text to toxic checking
                pipe = pipeline("text-classification", model="unitary/toxic-bert")
                logging.info(f'{pipe(translated_text.text)[0]} by {author}')
                if pipe(translated_text.text)[0]['score'] > 0.85:
                    reply = "This is warning {}.  {} please don't use abusive words!".format(
                        warnings + 1, author)
                    database[colletion_name].update_one(
                        {"user_id": update.message.from_user.id},
                        {"$set": {
                            "warnings": warnings + 1
                        }})
                    if warnings > 2:
                        try:
                            await context.bot.delete_message(chat_id=update.effective_chat.id,
                                                             message_id=update.message.message_id)
                            await context.bot.send_message(chat_id=update.effective_chat.id,
                                                           text="You violated our rules")
                            logging.info(f"Removed {author}")
                            await context.bot.ban_chat_member(chat_id=update.effective_chat.id,
                                                              user_id=update.message.from_user.id)
                            database[colletion_name].delete_one({"user_id": update.message.from_user.id})
                        except Exception as e:
                            logging.error(f'Error removing {author}', exc_info=context.error)
                    else:
                        await context.bot.delete_message(chat_id=update.effective_chat.id,
                                                         message_id=update.message.message_id)
                        await context.bot.send_message(chat_id=update.effective_chat.id,
                                                       text=reply)
            else:
                pipe = pipeline("text-classification", model="unitary/toxic-bert")
                logging.info(f'{pipe(update.message.text)[0]} by {author}')
                if pipe(update.message.text)[0]['score'] > 0.85:
                    reply = "This is warning {}.  {} please don't use abusive words!".format(
                        warnings + 1, author)
                    database[colletion_name].update_one(
                        {"user_id": update.message.from_user.id},
                        {"$set": {
                            "warnings": warnings + 1
                        }})
                    if warnings > 2:
                        try:
                            await context.bot.delete_message(chat_id=update.effective_chat.id,
                                                             message_id=update.message.message_id)
                            await context.bot.send_message(chat_id=update.effective_chat.id,
                                                           text="You violated our rules")
                            logging.info(f"Removed {author}")
                            await context.bot.ban_chat_member(chat_id=update.effective_chat.id,
                                                              user_id=update.message.from_user.id)
                            database[colletion_name].delete_one({"user_id": update.message.from_user.id})
                        except Exception as e:
                            logging.error(f'Error removing {author}', exc_info=context.error)
                    else:
                        await context.bot.delete_message(chat_id=update.effective_chat.id,
                                                         message_id=update.message.message_id)
                        await context.bot.send_message(chat_id=update.effective_chat.id,
                                                       text=reply)
    except Exception as e:
        logging.error(f'Error occurred while handling the text by user {author}', exc_info=context.error)


# stickers
async def echo_sticker(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    This function avoids the spamming of the sticker
    """
    author = update.message.from_user.first_name
    try:

        # Check if the user exists in the database, if not add the user
        user_data = database[colletion_name].find_one(
            {"user_id": update.message.from_user.id})
        if not user_data:
            user_data = {"user_id": update.message.from_user.id, "user_name": author, "warnings": 0}
            database[colletion_name].insert_one(user_data)

        warnings = user_data["warnings"]

        # Your existing code for handling stickers...
        reply = "This is warning {}.  {} Sending stickers are not allowed".format(
            warnings + 1, author)
        if warnings > 2:
            try:
                await context.bot.delete_message(chat_id=update.effective_chat.id,
                                                 message_id=update.message.message_id)
                await context.bot.send_message(chat_id=update.effective_chat.id,
                                               text="You violated our rules")
                await context.bot.ban_chat_member(chat_id=update.effective_chat.id,
                                                  user_id=update.message.from_user.id)
                logging.info(f"Removed {author}")
                database[colletion_name].delete_one({"user_id": update.message.from_user.id})
            except Exception as e:
                logging.error(f'Error removing {author}', exc_info=context.error)
        else:
            await context.bot.delete_message(chat_id=update.effective_chat.id,
                                             message_id=update.message.message_id)
            await context.bot.send_message(chat_id=update.effective_chat.id,
                                           text=reply)

        # Update the warning counter for the user
        database[colletion_name].update_one({"user_id": update.message.from_user.id},
                                            {"$set": {
                                                "warnings": warnings + 1
                                            }})
    except Exception as e:
        logging.error(f'Error occurred while handling sticker by user {author}', exc_info=context.error)


# Voice
async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    This function analyze the voice and if found toxic then deletes it and give the user the desired warning
    """
    author = update.message.from_user.first_name
    try:
        logging.info(f"Voice processing initiated by {author}")
        file_id = update.message.voice.file_id
        voice_note_file = await context.bot.get_file(file_id)
        logging.info(voice_note_file.file_path)
        logging.info(f'Voice send by {author} voice file is {voice_note_file.file_path}')

        audio_url = voice_note_file.file_path
        response = requests.get(audio_url)

        # Fetching data from the url

        if response.status_code == 200:
            with open('voice_message.ogg', 'wb') as f:
                f.write(response.content)
            ogg_file = os.path.join(os.getcwd(), 'voice_message.ogg')
            wav_file = os.path.join(os.getcwd(), 'temp_voice.wav')
            oga_file = AudioSegment.from_file(ogg_file, format="ogg")

            # Export it as a .wav file
            oga_file.export(wav_file, format="wav")
            logging.info("Exported")
            recognizer = sr.Recognizer()
            audio_file = wav_file
            with sr.AudioFile(audio_file) as source:
                audio_data = recognizer.record(source)

            # Trying audio analysis
            try:
                reply = recognizer.recognize_google(audio_data)
                try:
                    pipe = pipeline("text-classification", model="unitary/toxic-bert")
                    logging.info(f'{pipe(reply)[0]} by {author}')
                    if pipe(reply)[0]['score'] > 0.85:
                        reply = "This is warning.  {} you used--> {} words which are offencive!".format(author, reply)
                        await context.bot.send_message(chat_id=update.effective_chat.id,
                                                       text=reply)
                        await context.bot.delete_message(
                            chat_id=update.effective_chat.id,
                            message_id=update.message.message_id)
                    else:
                        reply = "You said --> {}".format(reply)
                        await context.bot.send_message(chat_id=update.effective_chat.id,
                                                       text=reply)
                except Exception as e:
                    logging.error(f'Error occurred while handling the text by user {author}', exc_info=context.error)
            except sr.UnknownValueError:
                logging.info("Google Web Speech Recognition could not understand voice")

            os.remove(ogg_file)
            os.remove(wav_file)
        else:
            logging.info(f"Failed to download the audio. Status code: {response.status_code}")

    except Exception as e:
        logging.error(f'Error while handling voice by {author} {e}', exc_info=context.error)


async def photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    This function analyze the photo and if found toxic or nude content then deletes it and give the user the desired warning
    """
    author = update.message.from_user.first_name
    try:
        logging.info(f"Image processing initiated by {author}")
        pipe = pipeline("image-to-text", model="Salesforce/blip-image-captioning-large")
        logging.info(update.message.photo[-1])
        image_id = update.message.photo[-1].file_id
        image_file = await context.bot.get_file(image_id)
        image_data = pipe(image_file.file_path)[0]['generated_text']

        pipe2 = pipeline("text-classification", model="unitary/toxic-bert")
        logging.info(f'{pipe2(image_data)[0]} by {author}')
        if pipe2(image_data)[0]['score'] > 0.85:
            await context.bot.send_message(chat_id=update.effective_chat.id,
                                           text=f"Your image implies to {image_data} which is toxic!")
            await context.bot.delete_message(
                chat_id=update.effective_chat.id,
                message_id=update.message.message_id)
        else:
            await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Your image implies to {image_data}")

    except Exception as e:
        logging.error(f"Error occurred while analysing photo{e}", exc_info=context.error)


# Audio  //Same as voice but the difference is here its .mp3 not .ogg
async def handle_audio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    author = update.message.from_user.first_name
    try:
        logging.info(f"Audio processing initiated by {author}")
        file_id = update.message.audio.file_id
        audio_note_file = await context.bot.get_file(file_id)
        logging.info(f'Audio send by {author} audio file is {audio_note_file.file_path}')
        audio_url = audio_note_file.file_path
        response = requests.get(audio_url, stream=True)

        if response.status_code == 200:
            with open('audio_message.mp3', 'wb') as f:
                f.write(response.content)
            mp3_file_path = os.path.join(os.getcwd(), 'audio_message.mp3')
            wav_file = os.path.join(os.getcwd(), 'temp_audio.wav')
            mp3_file = AudioSegment.from_file(mp3_file_path, format="mp3")
            mp3_file.export(wav_file, format="wav")
            logging.info("Exported")
            recognizer = sr.Recognizer()
            audio_file = wav_file
            with sr.AudioFile(audio_file) as source:
                audio_data = recognizer.record(source)

            try:
                reply = recognizer.recognize_google(audio_data)
                logging.info(reply)
                try:
                    pipe = pipeline("text-classification", model="unitary/toxic-bert")
                    logging.info(f'{pipe(reply)[0]} by {author}')

                    if pipe(reply)[0]['score'] > 0.85:
                        reply = "This is warning.  {} you used --> {} words which are offencive!".format(author, reply)
                        await context.bot.send_message(chat_id=update.effective_chat.id,
                                                       text=reply)
                        await context.bot.delete_message(
                            chat_id=update.effective_chat.id,
                            message_id=update.message.message_id)
                    else:
                        reply = "You said --> {}".format(reply)
                        await context.bot.send_message(chat_id=update.effective_chat.id,
                                                       text=reply)
                except Exception as e:
                    logging.error(f'Error occurred while handling the text by user {author}', exc_info=context.error)
            except sr.UnknownValueError:
                logging.info("Google Web Speech Recognition could not understand audio")
            os.remove(mp3_file)
            os.remove(wav_file)
            await context.bot.send_message(chat_id=update.effective_chat.id,
                                           text=f"Your audio is {reply}")
        else:
            logging.info(f"Failed to download the audio. Status code: {response.status_code}")


    except Exception as e:
        logging.error(f'Error while handling audio by {author} {e}', exc_info=context.error)
