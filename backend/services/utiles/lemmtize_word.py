import nltk
from nltk.stem import WordNetLemmatizer
lemmatizer = WordNetLemmatizer()


def lemmatize_word(word):
    try:
        return lemmatizer.lemmatize(word.lower())
    except:
        return word.lower()