#importing libraries for the task
import nltk
import pandas as pd

#downloading vader lexicon
nltk.download("vader_lexicon")

#import the lexicon
from nltk.sentiment.vader import SentimentIntensityAnalyzer

#Creating the instance
sent_analyzer = SentimentIntensityAnalyzer()

#Converting text to lowercase
def lowercase (text):
    low = text.lower()
    return low

#Removing URLs
def remove_url (text):
    import re
    text_clean = re.sub(r'http\S+', '', text)
    return text_clean

#Removing usernames
def remove_un (text):
    import re
    text_mod = re.sub(r'@[^\s]+', '', text)
    return text_mod

#Applying vader to text
def vadering(text):
    scores = sent_analyzer.polarity_scores(text)
    return scores

#Formatting the output of the vader dictionary
def format_output(output_dict):

    for keys, values in output_dict.items():
        if (values >= 0.8) & (keys!='compound'):
            return keys

    polarity = "neu"

    if(output_dict['compound']>= 0.05):
        polarity = "pos"

    elif(output_dict['compound']<= -0.05):
        polarity = "neg"

    return polarity

# Read the data set
df = pd.read_csv("raw_data/test2.csv", sep=';')

#Cleaning & applying sentimental ponderation to the data
def sent_data(df: pd.DataFrame) -> pd.DataFrame:

    df = df.dropna()
    df = df.reset_index(drop=True)
    df['text'] = df.text.apply(lowercase)
    df['text'] = df.text.apply(remove_url)
    df['text'] = df.text.apply(remove_un)
    df['vader_dict'] = df.text.apply(vadering)
    df['polarity'] = df.vader_dict.apply(format_output)

    return df
