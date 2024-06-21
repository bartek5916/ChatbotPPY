import random
import json
import re

import torch
from torch import Tensor
from ModelHandler.model import Net
from ModelHandler.nltk_utils import bag_of_words, tokenize_text
from DataBase.DatabaseContext import ShippingManager


class ChatBot:
    def __init__(self, FILE="../data.pth"):
        # Sprawdza, czy dostępna jest karta graficzna CUDA, jeśli nie, używa CPU
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

        # Wczytuje plik z intencjami w formacie JSON
        with open('../intents.json', 'r', encoding="UTF-8") as f:
            self.intents = json.load(f)

        # Wczytuje dane modelu zapisane w pliku .pth
        data = torch.load(FILE)

        # Inicjalizuje parametry modelu
        self.input_size = data['input_size']
        self.output_size = data['output_size']
        self.hidden_size = data['hidden_size']
        self.list_of_words = data['list_of_words']
        self.tags = data['tags']
        model_state = data['model_state']

        # Inicjalizuje model sieci neuronowej i wczytuje jego stan
        self.model = Net(self.input_size, self.hidden_size, self.output_size).to(self.device)
        self.model.load_state_dict(model_state)
        self.model.eval()

        # Ustawia nazwę bota
        self.bot_name = "Szczepan - Kurierex"

    def get_response(self, sentence):
        # Tokenizuje zdanie użytkownika
        sentence = tokenize_text(sentence)

        # Zamienia zdanie na worek słów
        x = bag_of_words(sentence, self.list_of_words)
        x = x.reshape(1, x.shape[0])
        x = torch.from_numpy(x)

        # Przewiduje odpowiedź za pomocą modelu
        output = self.model(x)
        _, predicted = torch.max(output, dim=1)
        tag = self.tags[predicted.item()]

        # Oblicza prawdopodobieństwo przewidywanej odpowiedzi
        probs = torch.softmax(output, dim=1)
        prob = probs[0][predicted.item()]

        # Jeśli prawdopodobieństwo jest wystarczająco wysokie, zwraca odpowiedź
        if prob.item() > 0.75:
            for intent in self.intents['intents']:
                if tag == intent['tag']:
                    response = random.choice(intent['responses']) + '\n'
                    list = [tag, response]
                    return list
        else:
            return ("Niestety, nie rozumiem. Czy możesz powtórzyć?" + '\n')

    def check_shipment_number(self, shipment_number, tag_status):
        sm = ShippingManager()

        if shipment_number.lower() == "wyjdź":
            return "Operacja anulowana"
        elif tag_status == 'information':
            # Sprawdza, czy numer przesyłki jest poprawny
            if len(shipment_number) == 9 and shipment_number.startswith("PL") and shipment_number[
                                                                                  2:6].isdigit() and shipment_number.endswith(
                    "/SK"):
                return sm.get_shipment_by_id(shipment_number)
            else:
                return "Niepoprawny format numeru przesyłki. Spróbuj ponownie."
        elif tag_status == "cancel_delivery":
            return sm.cancel_shipment(shipment_number)
        else:
            return "Niepoprawny format numeru przesyłki. Spróbuj ponownie."

    def get_pickup_points(self):
        sm = ShippingManager()
        return sm.get_pickup_points_excluding_home()

    def update_delivery_date(self):
        sm = ShippingManager()
        return sm.update_delivery_date()

    def check_for_word_number(self, sentence):
        # Sprawdza, czy w zdaniu jest słowo "numer"
        if "numer" in sentence:
            return True
        else:
            return False

    def check_for_word_points(self, sentence):
        # Sprawdza, czy w zdaniu jest słowo "punktów"
        if "punktów" in sentence:
            return True
        else:
            return False

    def check_for_word_date(self, sentence):
        # Sprawdza, czy w zdaniu jest słowo "datę"
        if "datę" in sentence:
            return True
        else:
            return False
