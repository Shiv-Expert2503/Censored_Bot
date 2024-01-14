# # # import librosa
# # # import numpy as np
# # # from transformers import pipeline
# # #
# # # # Replace 'audio_file.wav' with the path to your audio file
# # # audio_file = r"C:\Users\Dell\Downloads\file_23.oga"
# # #
# # # # Load the audio file using librosa
# # # audio, sample_rate = librosa.load(audio_file, sr=None)
# # #
# # # # Convert the audio data to a NumPy array
# # # audio_array = np.array(audio)
# # #
# # # # Print the shape of the audio array
# # # print("Shape of the audio array:", audio_array.shape)
# # # # Use a pipeline as a high-level helper
# # #
# # # pipe = pipeline("automatic-speech-recognition", model="openai/whisper-base")
# # # print(pipe(audio_array))
# # # import soundfile as sf
# # # import soundfile as sf
# # # import sounddevice as sd
# # #
# # # # Read the .npy file
# # # # audio_data = soundfile.read(r'C:\Users\Dell\Desktop\PROJECT\HTM\audio_array.npy')
# # # data, sample_rate = sf.read(r'C:\Users\Dell\Desktop\PROJECT\HTM\audio_array.npy')
# # #
# # # # Play the audio
# # # sd.play(data, sample_rate)
# # # sd.wait()
# # # import soundfile as sf
# # import os
# #
# # import torch
# # ###To play the audio
# # # # @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@22
# # # import sounddevice as sd
# # # import numpy as np
# # #
# # # # Replace 'audio_data.npy' with the path to your .npy file
# # # audio_file = r'C:\Users\Dell\Desktop\PROJECT\HTM\audio_array.npy'
# # #
# # # # Load the audio data from the .npy file
# # # audio_data = np.load(audio_file)
# # #
# # # # Play the audio using sounddevice
# # # sd.play(audio_data, samplerate=44100)  # Replace 44100 with the appropriate sample rate
# # #
# # # # Wait for the audio to finish playing
# # # sd.wait()
# #
# #
# #
# #
# # # import librosa
# # #
# # #
# # # mp3_file_1 = r'C:\Users\Dell\Desktop\PROJECT\HTM\temp_audio.mp3'
# # # mp3_file_2=r"C:\Users\Dell\Downloads\ElevenLabs_2023-10-25T08_07_23_Gigi_pre_s50_sb63_m1.mp3"
# # #
# # # # Load the MP3 file using librosa
# # # audio_data, sample_rate = librosa.load(mp3_file_1, sr=None)
# # # print(audio_data.shape)
# # #
# # # # Replace 'input.mp3' with the path to your input MP3 file
# #
# #
# #
# #
# #
# # # import librosa
# # # from transformers import pipeline
# # # import soundfile as sf
# # #
# # # # Specify the path to your audio file
# # # audio_file = r"C:\Users\Dell\Desktop\Recording (10).wav"
# # #
# # # # Read the audio file using librosa
# # # audio, sample_rate = librosa.load(audio_file, sr=None)
# # #
# # # print(audio.size)
# # # pipe = pipeline("automatic-speech-recognition", model="openai/whisper-medium")
# # # print(pipe(audio))
# #
# #
# #
# #
# # # from transformers import AutoProcessor, AutoModelForSpeechSeq2Seq
# # #
# # # # Load the processor and model
# # # processor = AutoProcessor.from_pretrained("openai/whisper-large-v2")
# # # model = AutoModelForSpeechSeq2Seq.from_pretrained("openai/whisper-large-v2")
# # #
# # # # Load and preprocess your audio data (replace 'audio.wav' with your audio file)
# # # # Ensure it matches the model's requirements for sampling rate, etc.
# # #
# # # # Tokenize the audio data using the processor
# # # inputs = processor(r"C:\Users\Dell\Desktop\temp_audio.wav", return_tensors="pt", padding="longest")
# # #
# # # # Perform inference to convert audio into text
# # # with torch.no_grad():
# # #     generated_ids = model.generate(inputs["input_features"])
# #
# # # Decode the generated text
# # # transcription = processor.batch_decode(generated_ids, skip_special_tokens=True)[0]
# # #
# # # # Print the transcription
# # # print(transcription)
# #
# # import speech_recognition as sr
# #
# # from pydub import AudioSegment
# #
# #
# # oga_file = r'C:\Users\Dell\Desktop\PROJECT\HTM\audio_message.mp3'
# # wav_file = os.path.join(os.getcwd(),'temp_audioxxx.wav')
# # # # Load the .oga file
# # # oga_file = AudioSegment.from_file(oga_file, format="ogg")
# # #
# # # # Export it as a .wav file
# # # oga_file.export(wav_file, format="wav")
# #
# #
# #
# #
# # mp3_file = AudioSegment.from_file(oga_file, format="mp3")
# #
# # # Export it as a WAV file
# # mp3_file.export(wav_file, format="wav")
# #
# #
# # # # import speech_recognition as sr
# # # recognizer = sr.Recognizer()
# # #
# # # audio_file = os.path.join(os.getcwd(),'temp_audioxxx.wav')
# # # with sr.AudioFile(audio_file) as source:
# # #     audio_data = recognizer.record(source)
# # #
# # # try:
# # #     text = recognizer.recognize_google(audio_data)  # Use Google Web Speech API
# # #     print("Google Web Speech Recognition: " + text)
# # # except sr.UnknownValueError:
# # #     print("Google Web Speech Recognition could not understand audio")
# # # except sr.RequestError as e:
# # #     print("Could not request results from Google Web Speech Recognition; {0}".format(e))
# #
#
# from googletrans import Translator
# from transformers import pipeline
#
# # Initialize the Translator
# translator = Translator()
#
# # Text to be translated
# text_to_translate = "abe oye bhen ke lode"
#
# # Detect the source language (optional)
# detected_language = translator.detect(text_to_translate).lang
#
# # Translate the text to a specific target language
# target_language = 'hi'  # French
# translated_text = translator.translate(text_to_translate, dest=target_language)
#
# # Print the translation
# print(f"Original Text: {text_to_translate} (Detected Language: {detected_language})")
# print(f"Translation to {target_language}: {translated_text.text}")
# # print(type(translated_text.text))
# pipe = pipeline("translation", model="Helsinki-NLP/opus-mt-hi-en")
# print(pipe(translated_text.text)[0])
# print(pipe(translated_text.text)[0]['translation_text'])
# # from translate import Translator
# #
# # # Initialize the Translator
# # translator = Translator(to_lang="en")  # Translate to French
# #
# # # Text to be translated
# # text_to_translate = "Bhai tu pagal h kya"
# #
# # # Translate the text
# # translation = translator.translate(text_to_translate)
# #
# # # Print the translation
# # print(f"Original Text: {text_to_translate}")
# # print(f"Translation: {translation}")
#
# # from microsofttranslator import Translator
# #
# # # Set your subscription key and endpoint (you'll need to sign up for Microsoft Azure)
# # subscription_key = 'c5b9bdbb-0437-4d9d-8707-4c6a17f2cc9a'
# # endpoint = '0717eac38f1949d991c287005139be40'
# #
# # translator = Translator(subscription_key, endpoint)
# #
# # # translator = Translator('<Your Client ID>', '<Your Client Secret>')
# # print( translator.translate("Hello", "pt"))
from googletrans import Translator
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ConversationHandler, MessageHandler, filters, \
    CallbackContext


# Define a function to handle the /add command
async def translate(update: Update, context: CallbackContext):
    await update.message.reply_text("Please enter the text:")
    return "GET_TEXT"


# Define a function to handle the first number input
async def get_trans_lang(update: Update, context: CallbackContext):
    try:
        context.user_data['text'] = str(update.message.text)
        await update.message.reply_text("Please enter the language you want it to get translated :")
        return "GET_LANG"
    except ValueError:
        await update.message.reply_text("Invalid Language")
        return "GET_TEXT"


# Define a function to handle the second number input and display the sum
async def get_text(update: Update, context: CallbackContext):
    try:
        target_language = update.message.text
        translator = Translator()
        text_to_translate = context.user_data['text']
        detected_language = translator.detect(text_to_translate).lang
        print(target_language)
        translated_text = translator.translate(text_to_translate, dest=target_language)
        print(f"Original Text: {text_to_translate} (Detected Language: {detected_language})")
        print(f"Translation to {target_language}: {translated_text.text}")
        await update.message.reply_text(f"The translation is {translated_text.text}")
    except ValueError:
        await update.message.reply_text("Invalid inputs.")
    return ConversationHandler.END


# Initialize your bot and set up the conversation handler
def main():
    bot_token = '6644344026:AAHmKqa6mubIGELIZ-7zlFWnjrf6NhCw1nw'
    application = ApplicationBuilder().token(bot_token).build()

    # Create a ConversationHandler for the /add command
    conversation_handler = ConversationHandler(
        entry_points=[CommandHandler('translate', translate)],
        states={
            "GET_TEXT": [MessageHandler(filters.TEXT & ~filters.COMMAND, get_trans_lang)],
            "GET_LANG": [MessageHandler(filters.TEXT & ~filters.COMMAND, get_text)]
        },
        fallbacks=[],
    )

    application.add_handler(conversation_handler)

    application.run_polling()


if __name__ == '__main__':
    main()
