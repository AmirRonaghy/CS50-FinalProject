# Custom module to translate dialog into selected language
# Guidance and instructions taken from:
# https://docs.microsoft.com/en-us/azure/cognitive-services/translator/tutorial-build-flask-app-translation-synthesis

# Import following modules to enable translation function
import os, requests, uuid, json

# Enter Azure subscription key and resource location
subscription_key = 'c56d4221599a4e11b570c2444ddf23a4'
location = 'westus'

# Flask route (translate-text) will supply original text (text_input) and translation language (language_output)
# When the submit button is pressed during conversation, the Ajax request in conversation.js will grab these values
# from the web app and pass them into the request
def get_translation(text_input, language_output):
    base_url = 'https://api.cognitive.microsofttranslator.com'
    path = '/translate?api-version=3.0'
    #Error checking
    print("Lang code: ",language_output)
    params = '&to=' + language_output
    constructed_url = base_url + path + params

    headers = {
        'Ocp-Apim-Subscription-Key': subscription_key,
        'Ocp-Apim-Subscription-Region': location,
        'Content-type': 'application/json',
        'X-ClientTraceId': str(uuid.uuid4())
    }

    # You can pass more than one object in body.
    body = [{
        'text' : text_input
    }]

    # Return text value from nested dictionary in JSON data
    response = requests.post(constructed_url, headers=headers, json=body)
    data = response.json()
    return data[0]["translations"][0]["text"]
