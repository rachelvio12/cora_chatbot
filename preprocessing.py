import re
import string
from Sastrawi.Stemmer.StemmerFactory import StemmerFactory

STOPWORDS = {
    "yang", "di", "ke", "dari", "untuk", "pada", "dengan", "dan", "atau",
    "ini", "itu", "saya", "anda", "ada", "tidak", "akan", "bisa", "apa",
    "bagaimana", "gimana", "cara", "mau", "tapi", "kalau", "jika", "adalah",
    "sih", "dong", "deh", "kok", "ya", "nya", "lah", "kah", "pun"
}

factory = StemmerFactory()
stemmer = factory.create_stemmer()


def case_folding(text):
    return text.lower()


def clean_text(text):
    text = re.sub(r"[%s]" % re.escape(string.punctuation), " ", text)
    text = re.sub(r"\d+", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def tokenize(text):
    return text.split()


def remove_stopwords(tokens):
    hasil = []
    for t in tokens:
        if t not in STOPWORDS:
            hasil.append(t)
    return hasil


def stemming(text):
    return stemmer.stem(text)


def preprocess(text):
    text = case_folding(text)
    text = clean_text(text)
    tokens = tokenize(text)
    tokens = remove_stopwords(tokens)
    text = " ".join(tokens)
    text = stemming(text)
    return text