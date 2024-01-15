import os

import requests
import speech_recognition as sr
from googletrans import Translator
from pydub import AudioSegment
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters, CallbackContext, \
    ConversationHandler

from database import set_up_connection
from logger import logging
from utils import languages_available, reply_text, photo, handle_audio, handle_voice, echo_sticker

####################################################################################################


li = []
i = 1
all_topics = [['/start', '/help', '/translate'], ['/translate_voice', '/audio_to_text'],
              ['/languages_available']]

database, colletion_name = set_up_connection()
#################################################################################################

# Initialising Everything

Token = Your_Bot_Token


# handling start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    This function works when user does /start
    @param update: The update query by the user
    @param context: The context is to define the returnn type of the update
    """
    author = update.message.from_user.first_name
    logging.info(f'Bot Started By user {author}')
    database[colletion_name].insert_one({author: "hello there"})

    reply = ("Hi! 👋 {}😃\n\n I'am all-in-one bot. I can detect spam and gives the particular user warnings, "
             "if warning exceeds more than 3 then i'll kick thet particular user. Type /command to see all commands"
             " available. \n\n Features available \n\n 1. Offensive/Faul Language Detection \n\n"
             " 2. Text_Translation \n\n 3.Voice to Text(Custom languages available) \n\n"
             " 4. Audio to Text (Custom languages available) \n\n 5. Spam Detection (Links/Stickers) \n\n "
             "6. Image Analysis").format(
        author)
    await context.bot.send_message(chat_id=update.effective_chat.id,
                                   text=reply)
    li.append(author)
    logging.info(f"DM by {author}")


# handling help command
async def help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Display help when user does /help
    """
    author = update.message.from_user.first_name
    logging.info(f"Help command activated by user {author}")
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Can't help at this moment kindly contact Shivansh personally!")


async def command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Display all available commands when user does /command
    """
    logging.info(all_topics)
    await context.bot.send_message(chat_id=update.effective_chat.id, text='Here are all the commands',
                                   reply_markup=ReplyKeyboardMarkup(keyboard=all_topics, one_time_keyboard=True))


##################################################################################################################
# This is the conversational translation

# Handling translate command
async def translate(update: Update, context: CallbackContext):
    await update.message.reply_text("Please enter the text:")
    return "GET_TEXT"


async def get_trans_lang(update: Update, context: CallbackContext):
    try:
        context.user_data['text'] = str(update.message.text)
        await update.message.reply_text(
            "Please enter the language you want it to get translated(Please see languages available and type their "
            "short forms) :")
        return "GET_LANG"
    except ValueError:
        await update.message.reply_text("Invalid Language")
        return "GET_TEXT"


async def get_text(update: Update, context: CallbackContext):
    try:
        logging.info("Get Text started")
        target_language = update.message.text
        translator = Translator()
        text_to_translate = context.user_data['text']
        detected_language = translator.detect(text_to_translate).lang

        translated_text = translator.translate(text_to_translate, dest=target_language)
        logging.info(f"Original Text: {text_to_translate} (Detected Language: {detected_language})")
        logging.info(f"Translation to {target_language}: {translated_text.text}")
        await update.message.reply_text(f"The translation is {translated_text.text}")
    except ValueError:
        logging.error("Error Occurred at translation of text ")
        await update.message.reply_text("Invalid inputs.")
    return ConversationHandler.END


#####################################################################################################################


####################################################################################################################
# Conversational voice translator
async def translate_voice(update: Update, context: CallbackContext):
    """
    @return : it returns the voice inputted by the user
    """
    author = update.message.from_user.first_name
    logging.info(f"Voice Translation activated by {author}")
    await update.message.reply_text("Please input your voice:")
    return "GET_VOICE"


async def get_trans_lang_voice(update: Update, context: CallbackContext):
    """
    This takes the language in which the voice needs to be translated
    @return : it returns the language in which the voice needs to be translated
    """
    try:
        author = update.message.from_user.first_name
        file_id = update.message.voice.file_id
        voice_note_file = await context.bot.get_file(file_id)
        logging.info(voice_note_file.file_path)
        logging.info(f'Voice send by {author} voice file is {voice_note_file.file_path}')
        context.user_data['voice'] = voice_note_file.file_path
        await update.message.reply_text(
            "Please enter the language you want it to get translated(Please see languages available and type their "
            "short forms) :")
        return "GET_LANG"
    except ValueError:
        await update.message.reply_text("Invalid Language")
        return "GET_VOICE"


async def get_translated_voice(update: Update, context: CallbackContext):
    """
    This functions returns the translation of the voice in the desired language
    """
    author = update.message.from_user.first_name
    try:
        logging.info("Voice_translation main process started")
        target_language = update.message.text
        audio_url = context.user_data['voice']
        logging.info(audio_url)
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

            reply = recognizer.recognize_google(audio_data)
            translator = Translator()
            text_to_translate = reply
            detected_language = translator.detect(text_to_translate).lang
            translated_text = translator.translate(text_to_translate, dest=target_language)
            logging.info(f"{author} Original Text: {text_to_translate} (Detected Language: {detected_language})")
            logging.info(f"{author} Translation to {target_language}: {translated_text.text}")
            await update.message.reply_text(f"The translation is {translated_text.text}")
            os.remove(ogg_file)
            os.remove(wav_file)
            logging.info("Removed")
    except Exception as e:
        await update.message.reply_text("Invalid inputs.")
        logging.error("Error while translating", exc_info=context.error)
    return ConversationHandler.END


######################################################################################################################

######################################################################################################################
# Conversational audio translater
async def translate_audio(update: Update, context: CallbackContext):
    author = update.message.from_user.first_name
    logging.info(f"Audio translation started by {author}")
    await update.message.reply_text("Please input audio: ")
    return "GET_AUDIO"


async def get_trans_lang_audio(update: Update, context: CallbackContext):
    author = update.message.from_user.first_name
    try:
        file_id = update.message.audio.file_id
        audio_note_file = await context.bot.get_file(file_id)
        logging.info(audio_note_file.file_path)
        logging.info(f'Audio send by {author} audio file is {audio_note_file.file_path}')
        audio_url = audio_note_file.file_path
        context.user_data['audio'] = audio_url
        await update.message.reply_text(
            "Please enter the language you want it to get translated(Please see languages available and type their "
            "short forms) :")
        return "GET_LANG"
    except ValueError:
        logging.info("User didn't entered the right language")
        await update.message.reply_text("Invalid Language")
        return "GET_AUDIO"


async def get_translated_audio(update: Update, context: CallbackContext):
    author = update.message.from_user.first_name
    try:
        logging.info("Main Translation Started")
        target_language = update.message.text
        audio_url = context.user_data['audio']
        logging.info(audio_url)
        response = requests.get(audio_url)
        # Fetching data from the url
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
            reply = recognizer.recognize_google(audio_data)
            translator = Translator()
            text_to_translate = reply
            detected_language = translator.detect(text_to_translate).lang
            # print(target_language)
            translated_text = translator.translate(text_to_translate, dest=target_language)
            logging.info(f"{author} Original Text: {text_to_translate} (Detected Language: {detected_language})")
            logging.info(f"{author} Translation to {target_language}: {translated_text.text}")
            await update.message.reply_text(f"The translation is {translated_text.text}")
            try:
                os.remove(mp3_file_path)
                os.remove(wav_file)
                logging.info("Removed")
            except Exception as e:
                logging.info("Error While Removing directary")

    except Exception as e:
        await update.message.reply_text("Invalid inputs.")
        logging.error("Error while translating", exc_info=context.error)
    return ConversationHandler.END


#####################################################################################################################

async def report(update: Update, context: CallbackContext):
    author = update.message.from_user.first_name
    logging.info(f"Report command started by {author}")
    await update.message.reply_text("Enter the username: ")
    return "GET_USERNAME"


async def make_report(update: Update, context: CallbackContext):
    author = update.message.from_user.first_name
    try:
        logging.info("Main Report started")
        username = update.message.text
        chat = await context.bot.get_chat(username)
        user_id = chat.id
        await update.message.reply_text(f"User is {user_id}")
        user_data = database[colletion_name].find_one(
            {"user_id": update.message.from_user.id})
        if not user_data:
            user_data = {"user_id": update.message.from_user.id, "user_name": author, "warnings": 0}
            database[colletion_name].insert_one(user_data)
        warnings = user_data["warnings"]
        database[colletion_name].update_one(
            {"user_id": update.message.from_user.id},
            {"$set": {
                "warnings": warnings + 1
            }})
    except ValueError:
        logging.error(f"Error occurred while reporting done by {author}", exc_info=context.error)
        await update.message.reply_text("Invalid inputs.")
    return ConversationHandler.END


# For unknown commands
async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    This handler is to handle unknown commands inputted by the user
    """
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="This command doesn't exist. Please try with valid commands")


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    """
    Custom error handler that handles exceptions raised by the user
    """
    logging.error("Exception while handling an update:", exc_info=context.error)


# Main Function
def main():
    application = ApplicationBuilder().token(Token).build()

    # Making command handler for start
    application.add_handler(CommandHandler('start', start))
    # Making command handler for help
    application.add_handler(CommandHandler('help', help))

    application.add_handler(CommandHandler('command', command))

    application.add_handler(CommandHandler('languages_available', languages_available))

    # Making command handler for translate in the conversation
    conversation_handler = ConversationHandler(
        entry_points=[CommandHandler('translate', translate)],
        states={
            "GET_TEXT": [MessageHandler(filters.TEXT & ~filters.COMMAND, get_trans_lang)],
            "GET_LANG": [MessageHandler(filters.TEXT & ~filters.COMMAND, get_text)]
        },
        fallbacks=[],
    )

    application.add_handler(conversation_handler)

    report_handler = ConversationHandler(
        entry_points=[CommandHandler('report', report)],
        states={
            "GET_USERNAME": [MessageHandler(filters.TEXT & ~filters.COMMAND, make_report)],
        },
        fallbacks=[],
    )
    application.add_handler(report_handler)

    # This is conversational voice translation

    conversation_handler_voice = ConversationHandler(
        entry_points=[CommandHandler('translate_voice', translate_voice)],
        states={
            "GET_VOICE": [MessageHandler(filters.VOICE & ~filters.COMMAND, get_trans_lang_voice)],
            "GET_LANG": [MessageHandler(filters.TEXT & ~filters.COMMAND, get_translated_voice)]
        },
        fallbacks=[],
    )

    application.add_handler(conversation_handler_voice)

    # This is conversational audio translation

    conversation_handler_audio = ConversationHandler(
        entry_points=[CommandHandler('audio_to_text', translate_audio)],
        states={
            "GET_AUDIO": [MessageHandler(filters.AUDIO & ~filters.COMMAND, get_trans_lang_audio)],
            "GET_LANG": [MessageHandler(filters.TEXT & ~filters.COMMAND, get_translated_audio)]
        },
        fallbacks=[],
    )

    application.add_handler(conversation_handler_audio)

    # Making message handler
    application.add_handler(MessageHandler(filters.TEXT, reply_text))
    # Making sticker handler
    application.add_handler(MessageHandler(filters.Sticker.ALL, echo_sticker))
    application.add_handler(MessageHandler(filters.PHOTO, photo))
    # Making voice handler
    application.add_handler(MessageHandler(filters.VOICE, handle_voice))
    # Making voice handler
    application.add_handler(MessageHandler(filters.AUDIO, handle_audio))
    # application.add_error_handler(error)
    application.add_error_handler(error_handler)
    # unknown command handler
    application.add_handler(MessageHandler(filters.COMMAND, unknown))
    print('Application Started')
    application.run_polling()


if __name__ == '__main__':
    main()
