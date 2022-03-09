# Code for creating and training deep learning model to predict conversational intents
# Guidance and instructions for model development and training approach were taken from following sources:
# How To Create A Chatbot with Python & Deep Learning In Less Than An Hour -- https://towardsdatascience.com/how-to-create-a-chatbot-with-python-deep-learning-in-less-than-an-hour-56a063bdfc44
# Create a Deep Learning Machine Learning Chatbot with Python and Flask -- https://www.youtube.com/watch?v=8HifpykuTI4&t=20s
# Intelligent AI Chatbot in Python -- https://www.youtube.com/watch?v=1lwddP0KUEg

# Import nltk for preprocessing text data
# Import json to load intents data from json files into Python
# Import pickle to load words and classes into pkl files to be used for model training
# Import numpy to perform linear algebra operations on text data
# Import keras to create deep learning model
import nltk
nltk.download('punkt')
nltk.download('wordnet')
from nltk.stem import WordNetLemmatizer
lemmatizer = WordNetLemmatizer()
import json
import pickle
import numpy as np
import tensorflow
from tensorflow import keras
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Activation, Dropout
from tensorflow.keras.optimizers import SGD
import random

# Create lists to store identified tags, patterns and tag-pattern pairs
words=[]
classes = []
documents = []

# Create list to enable removal of punctuation
ignore_words = ['?', '!', ',', '.']

# Open json file and load intents data into Python
data_file = open('intents.json').read()
intents = json.loads(data_file)

# Iterate through intents in json file to extract patterns for each intent
for intent in intents['intents']:
    for pattern in intent['patterns']:
        # Tokenize each pattern (i.e., splits into individual words) and store words in words list
        w = nltk.word_tokenize(pattern)
        words.extend(w)
        # Add each identified tag-patten pair as a tuple to documents list
        documents.append((w, intent['tag']))
        # Add each unique tag to classes list
        if intent['tag'] not in classes:
            classes.append(intent['tag'])

# Lowercase, lemmatize (i.e., convert words to their base meaning) and remove punctuation from patterns
words = [lemmatizer.lemmatize(w.lower()) for w in words if w not in ignore_words]

# Sort tags and patterns lists and remove any redundancies
words = sorted(list(set(words)))
classes = sorted(list(set(classes)))

# Print out results for error checking
print (len(documents), "documents")
print (len(classes), "classes", classes)
print (len(words), "unique lemmatized words", words)

# Store tags and patterns in pkl files for use in model training
pickle.dump(words,open('words.pkl','wb'))
pickle.dump(classes,open('classes.pkl','wb'))

# Initialize training data
training = []

# Initialize outputs as list of zeros matching number of tags
output_empty = [0] * len(classes)

# Iterate through each tag-pattern pair
for doc in documents:
    # Initialize bag of words for each pair
    bag = []
    # List of tokenized words for the pattern
    word_patterns = doc[0]
    # Lemmatize (i.e., create base word) and lower case each word in attempt to represent related words
    word_patterns = [lemmatizer.lemmatize(word.lower()) for word in word_patterns]

    # Create bag of words array with 1 if given word is found in current pattern
    for w in words:
        bag.append(1) if w in word_patterns else bag.append(0)

    # Create list of outputs to represent each tag
    output_row = list(output_empty)
    # Change output to '1' for current tag (for each pattern) and '0' for every other tag
    output_row[classes.index(doc[1])] = 1
    # Add bag of words and tag output as a pair (i.e., tuple) to training list as label-feature pair
    training.append([bag, output_row])

# Shuffle features and turn them into a numpy array
random.shuffle(training)
training = np.array(training)

# Split array into training and test sets; X: patterns, Y: intents
train_x = list(training[:,0])
train_y = list(training[:,1])
print("Training data created")

# Use sequential neural network model in Keras as basis for deep learning model
# Sequential model is appropriate when each layer of neural network has one input and one output tensor
# Source -- https://keras.io/guides/sequential_model/

# Create sequential model and add the three layers specified below
model = Sequential()

# First layer is input layer with 128 neurons and input shape equal to size of training set
# ReLU = rectified linear activation function; generates output for node based on weighted input
# Use dropout to prevent model overfitting; dropout rate of 0.5 removes 50% of all inputs to layer
# https://machinelearningmastery.com/rectified-linear-activation-function-for-deep-learning-neural-networks/
# https://machinelearningmastery.com/how-to-reduce-overfitting-with-dropout-regularization-in-keras/
model.add(Dense(128, input_shape=(len(train_x[0]),), activation='relu'))
model.add(Dropout(0.5))

# Second layer has 64 neurons
model.add(Dense(64, activation='relu'))
model.add(Dropout(0.5))

# Third layer is output layer with number of neurons equal to number of intents to predict output intent
# Softmax function converts outputs from weighted sum values to probabilities that sum to 1
# https://machinelearningmastery.com/softmax-activation-function-with-python/
model.add(Dense(len(train_y[0]), activation='softmax'))

# Compile model using stochastic gradient descent with Nesterov accelerated gradient (recommended by Jere Xu)
# SGD is most efficient algorithm for training neural networks
# Cross-entropy is loss function for classification problems
# https://machinelearningmastery.com/difference-between-backpropagation-and-stochastic-gradient-descent/
sgd = SGD(lr=0.01, decay=1e-6, momentum=0.9, nesterov=True)
model.compile(loss='categorical_crossentropy', optimizer=sgd, metrics=['accuracy'])

# Fit model to training set and then apply it to test set to evaluate its accuracy
# Epoch is one pass through entire training set
# Batch size is number of dataset rows that must be processed before weights are adjusted
# https://machinelearningmastery.com/tutorial-first-neural-network-python-keras/
hist = model.fit(np.array(train_x), np.array(train_y), epochs=200, batch_size=5, verbose=1)

# Save model after training
model.save('chatbot_model.h5', hist)
print("model created")
