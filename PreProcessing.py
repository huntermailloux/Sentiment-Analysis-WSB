import re
import numpy as np
import pandas as pd
import kagglehub
import string
import contractions
from nltk.corpus import stopwords

# Download dataset from Kaggle (https://www.kaggle.com/datasets/gpreda/wallstreetbets-2022)
path = kagglehub.dataset_download("gpreda/wallstreetbets-2022")
data = pd.read_csv(f"{path}/wallstreetbets_2022.csv", encoding="utf-8", dtype={"body": str}, low_memory=False)

# Extracts the date of the post from the Kaggle dataset.
if "timestamp" in data.columns:
    data["date"] = pd.to_datetime(data["timestamp"]).dt.date  # Keeps only YYYY-MM-DD and not the time as well.

# Loads the symbols from the symbol.csv
symbolsCSV = pd.read_csv("symbols.csv", encoding="utf-8", usecols=["Symbol"])
validSymbols = set(symbolsCSV["Symbol"].astype(str).str.upper())

# Keeps only the required columns in the dataset.
data = data[["date", "body"]].dropna(subset=["body"])

# Filters unated posts that are very common occurences on the r/WallStreetBets subreddit.
data.replace(to_replace='None', value=np.nan).dropna()
data = data[~data["body"].str.contains("Your daily trading discussion thread.")]
data = data[~data["body"].str.contains("Your daily hype thread.")]
data = data[~data["body"].str.contains("Your weekend discussion thread.")]
data = data[~data["body"].str.contains("Welcome to WSB")]
data = data[~data["body"].str.contains(r"Inductions\n")]
data = data[~data["body"].str.contains("This is an old Yacht Club thread")]
data = data[~data["body"].str.contains(r"\*Processing img")]
data = data[~data["body"].str.contains("You already have a bet")]
data = data[data["body"].str.contains(" ")]

# Sets our variables and compiles our regex.
urlRegex = re.compile(r"https?://\S+") 
symbolRegex = re.compile(r'(?<!\w)\b[A-Z]{2,5}\b(?!\w)')
imgemoteRegex = re.compile(r"imgemotet\w*\d*")

# Creates our stopwords library.
stopWords = set(stopwords.words("english"))

# Function the removes all non ASCII charcters (used to remove emojis)
def removeNonASCII(text):
    return ''.join(char for char in text if ord(char) < 128)

# Function to complete preprocessing on the text.
def preProcessText(s):
    s = s.lower() # Make post lowercase
    s = contractions.fix(s) # Fix contractions within the post
    s = urlRegex.sub("", s) # Remove url's from the posts
    s = removeNonASCII(s) # Remove all non ASCII chracters from posts (emojis)
    s = "".join(char for char in s 
                if char not in string.punctuation)  # Remove punctuation from the posts
    s = " ".join(word for word in s.split() 
                 if word not in stopWords) # Removes stop words
    s = imgemoteRegex.sub("", s) 
    
    return s # Returns the processed post.

# Function that checks if a post is made up of more then 25% numbers.
def checkNumbers(post):
    words = post.split()
    num_count = sum(word.isdigit() for word in words)
    return (num_count / len(words)) > 0.25 

# Function to extract stock symbols from posts.
def extractSymbols(post):
    if not isinstance(post, str):
        return []
    return list(set(symbol for symbol in symbolRegex.findall(post.upper()) if symbol in validSymbols))

# Applys text preprocessing on each post.
data["post"] = data["body"].astype(str).apply(preProcessText)
data = data[data["post"].str.split().str.len() > 1] # Checks if the post has 2 or more words.

# Extracts stock symbols from posts.
data["symbols"] = data["post"].apply(extractSymbols)

# Keeps posts that mention at least one valid ticker (removes the other ones)
data = data[data["symbols"].str.len() > 0]
data = data[~data["post"].apply(checkNumbers)] # Calls the check numbers functions.

# Creates columns for our processed csv.
columns = ["date", "post", "symbols"]
data[columns].to_csv("processedWSBposts.csv", index=False, encoding="utf-8-sig") # Save to csv

print(f"Data saved to processedWSBposts.csv")

