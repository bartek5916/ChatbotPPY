import nltk
import numpy as np
from stempel import StempelStemmer
from nltk.stem.porter import PorterStemmer

# Tworzymy domyślny obiekt stemmera Stempel, który będzie używany do stemmingu (sprowadzania słów do ich rdzeni).
stemmer = StempelStemmer.default()

# Funkcja do stemmingu tekstu.
# Przyjmuje tekst, zamienia go na małe litery i zwraca jego wersję stemmowaną.
def stem_text(text):
    return stemmer.stem(text.lower())

# Funkcja do tokenizacji tekstu.
# Przyjmuje tekst i zwraca listę tokenów (słów) w nim zawartych.
def tokenize_text(text):
    return nltk.word_tokenize(text)

# Funkcja do tworzenia worka słów (bag of words).
# Przyjmuje tokenizowany tekst i listę słów, a następnie tworzy wektor, który reprezentuje,
# które słowa z listy występują w tokenizowanym tekście.
def bag_of_words(tokenized_text, word_list):
    # Przeprowadza stemming każdego tokenu w tokenizowanym tekście.
    tokenized_text = [stem_text(w) for w in tokenized_text]
    # Tworzy wektor o długości listy słów, wypełniony zerami.
    bag = np.zeros(len(word_list), dtype=np.float32)

    # Iteruje przez listę słów. Jeśli słowo znajduje się w tokenizowanym tekście,
    # ustawia odpowiedni indeks wektora na 1.
    for i,w, in enumerate(word_list):
        if w in tokenized_text:
            bag[i] = 1.0
    return bag
