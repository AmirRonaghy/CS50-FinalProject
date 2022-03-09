# Code for applying deep learning model to chatbot dialog to predict conservational intents
# Guidance and instructions for functions below were taken from the following sources:
# How To Create A Chatbot with Python & Deep Learning In Less Than An Hour -- https://towardsdatascience.com/how-to-create-a-chatbot-with-python-deep-learning-in-less-than-an-hour-56a063bdfc44
# Create a Deep Learning Machine Learning Chatbot with Python and Flask -- https://www.youtube.com/watch?v=8HifpykuTI4&t=20s
# Intelligent AI Chatbot in Python -- https://www.youtube.com/watch?v=1lwddP0KUEg

# Import nltk for preprocessing text data
# Import json to load intents data from json files into Python
# Import pickle to load words and classes from pkl files into Python
# Import numpy to perform linear algebra operations on text data
import nltk
from nltk.stem import WordNetLemmatizer
lemmatizer = WordNetLemmatizer()
import pickle
import json
import numpy as np
import random

# Use Keras load model to open deep learning model created in chatbot.py
from keras.models import load_model
model = load_model('chatbot_model.h5')

# Load intents data into Python
intents = json.loads(open('intents.json').read())

# Load preprocessed patterns and intents into Python
words = pickle.load(open('words.pkl','rb'))
classes = pickle.load(open('classes.pkl','rb'))

# Function to preprocess student dialog with chatbot
# Tokenize text to separate it into distinct words
# Lowercase and lemmatize (i.e., convert to base word) words
def clean_up_sentence(sentence):
    sentence_words = nltk.word_tokenize(sentence)
    sentence_words = [lemmatizer.lemmatize(word.lower()) for word in sentence_words]
    return sentence_words

# Function to create bag of words array for predicting intents
# Returns 1 for each word in the bag that exists in the sentence
def bag_of_words(sentence):
    # Preprocess dialog sent to chatbot using function defined above
    sentence_words = clean_up_sentence(sentence)
    # Initialize bag of words matrix containing preprocessed patterns from intents data
    bag = [0] * len(words)
    # Iterate through words from student dialog
    for s in sentence_words:
        # Iterate through patterns and respective indices
        for i, w in enumerate(words):
            # Assign value of 1 whenever word is found in dialog
            if w == s:
                bag[i] = 1

    # Return bag of words as numpy array
    return(np.array(bag))

# Function to output list of intents and probabilities for each one
# Filters out intents with probabilities below 0.25 to avoid overfitting
def predict_class(sentence):
    # Create bag of words for conversational dialog using function defined abovre
    bow = bag_of_words(sentence)
    # Apply model to list containing bag of words from dialog and store predictive results
    res = model.predict(np.array([bow]))[0]
    # Set error threshold to 0.25 to filter out predictions with low probabilities
    ERROR_THRESHOLD = 0.25
    # Use enumerate to iterate through intents and their probabilities; removes intents with probabilities < 0.25
    results = [[i, r] for i, r in enumerate(res) if r > ERROR_THRESHOLD]
    # Sort intents by strength of probability (i.e., index 1 of each i,r pair)
    results.sort(key=lambda x: x[1], reverse=True)
    # Create formatted list of intents and probabilities
    return_list = []
    for r in results:
        # Append intents (index 0 of results) and probabilities (index 1) in string format to formatted list
        return_list.append({"intent": classes[r[0]], "probability": str(r[1])})
    return return_list

# Function to randomly selected response for intent
def getResponse(ints, intents_json):
    # Store predicted intent (index 0 of prediction result) in variable
    tag = ints[0]['intent']    #
    # Iterate through intents in json file
    list_of_intents = intents_json['intents']
    for i in list_of_intents:
        # If predicted intent is found in json file, generate randomly selected response
        if(i['tag']== tag):
            result = random.choice(i['responses'])
            break
        # Else ask for clarification
        else:
            result = "Sorry, I didn't understand. Could you please rephrase the question? Or maybe try asking another question."
    return result

# Function to generate response to student dialog based on predicted intent
def chatbot_response(msg):
    ints = predict_class(msg)
    res = getResponse(ints, intents)
    return res
