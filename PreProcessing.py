import re
import numpy as np
import pandas as pd
import kagglehub
from nltk.corpus import stopwords
import string

path = kagglehub.dataset_download("gpreda/reddit-wallstreetsbets-posts")

data = pd.read_csv(path + "\\reddit_wsb.csv")
data = data.replace(to_replace='None', value=np.nan).dropna()
data = data[~data["body"].str.contains("Your daily trading discussion thread.")]
data = data[~data["body"].str.contains("Your daily hype thread.")]
data = data[~data["body"].str.contains("Your weekend discussion thread.")]
data = data[~data["body"].str.contains("Welcome to WSB")]
data = data[~data["body"].str.contains(r"Inductions\n")]
data = data[~data["body"].str.contains("This is an old Yacht Club thread")]
data = data[~data["body"].str.contains(r"\*Processing img")]
data = data[data["body"].str.contains(" ")]

def text_preprocessing(s):
    """
    - Lowercase the sentence
    - Change "'t" to "not"
    - Remove "@name"
    - Isolate and remove punctuations
    - Remove other special characters
    - Remove stop words except "not" and "can"
    """
    #Lower Case
    s = s.lower()
    # Change 't to 'not'
    s = re.sub(r"'t", " not", s)
    #Removing Punctuation
    s ="".join([i for i in s if i not in string.punctuation])
    
    # Remove stopwords except 'not' and 'can'
    s = " ".join([word for word in s.split()
                  if word not in stopwords.words('english')
                  or word in ['not', 'can']])
    
    s = " ".join([word for word in s.split(" ") if ('https' not in word)])
    
    return s

data["preprocessed_title"] = data["title"].apply(text_preprocessing)
data["preprocessed_body"] = data["body"].apply(text_preprocessing)