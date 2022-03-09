# Custom module to provide text-to-speech functionality for translated dialog
# Guidance and instructions taken from:
# https://docs.microsoft.com/en-us/azure/cognitive-services/speech-service/get-started-text-to-speech
# https://github.com/Azure-Samples/cognitive-services-speech-sdk/blob/master/samples/python/console/speech_synthesis_sample.py

# Import Azure Speech SDK
import azure.cognitiveservices.speech as speechsdk

from flask import session
import time

# Retrieve Azure subscription key and service region
speech_key, service_region = "5ec2f01a05ff49a88acaff82de29a859", "westus"

# Define function to convert translated dialog to speech selected language and voice
# Pass translated dialog, selected language and voice into function as parameters
def synthesize_speech(text, language, voice):
    # Create speech config instance with Azure subscription key and service region.
    speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=service_region)

    # Store selected language and voice in speech config
    speech_config.speech_synthesis_language = language
    speech_config.speech_synthesis_voice_name = voice

    # Set synthesis output format to mp3
    speech_config.set_speech_synthesis_output_format(speechsdk.SpeechSynthesisOutputFormat.Audio16Khz32KBitRateMonoMp3)

    # Create speech synthesizer with audio output stored in mp3 file
    datetime = str(time.time())
    session["audio-file"] = f"outputaudio_{datetime}.mp3"
    file = "static/" + session["audio-file"]
    file_config = speechsdk.audio.AudioOutputConfig(filename=file)
    speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=file_config)

    # Return synthesized speech for translated text
    result = speech_synthesizer.speak_text_async(text).get()
    return result
