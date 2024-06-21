import json  # Importowanie biblioteki do pracy z plikami JSON.
import numpy as np  # Importowanie biblioteki do pracy z tablicami numerycznymi.
import torch  # Importowanie głównej biblioteki PyTorch.
import torch.nn as nn  # Importowanie modułu sieci neuronowych w PyTorch.
from torch.utils.data import Dataset, DataLoader  # Importowanie narzędzi do pracy z danymi w PyTorch.
from ModelHandler.nltk_utils import tokenize_text, stem_text, bag_of_words  # Importowanie funkcji pomocniczych do przetwarzania tekstu.
from ModelHandler.model import Net  # Importowanie modelu sieci neuronowej.

# Wczytywanie danych z pliku JSON.
with open('../intents.json', 'r', encoding="UTF-8") as f:
    intents = json.load(f)

# Inicjalizacja listy słów, tagów i par (słowa, tagi).
list_of_words = []
tags = []
xy = []

# Przetwarzanie intencji z pliku JSON.
for intent in intents['intents']:
    tag = intent['tag']  # Pobieranie tagu intencji.
    tags.append(tag)
    for pattern in intent['patterns']:
        w = tokenize_text(pattern)  # Tokenizacja wzorca.
        list_of_words.extend(w)
        xy.append((w, tag))

# Lista słów do ignorowania.
ignore_words = ['?', '!', '.', ',']
# Przetwarzanie listy słów (stemmowanie i usuwanie znaków interpunkcyjnych).
list_of_words = [stem_text(w) for w in list_of_words if w not in ignore_words]
list_of_words = sorted(list(set(list_of_words)))
tags = sorted(list(set(tags)))

# Inicjalizacja danych treningowych.
x_train = []
y_train = []

# Tworzenie worka słów i odpowiadających im etykiet.
for (pattern_sentence, tag) in xy:
    bag = bag_of_words(pattern_sentence, list_of_words)
    x_train.append(bag)

    label = tags.index(tag)
    y_train.append(label)

x_train = np.array(x_train)
y_train = np.array(y_train)

# Definicja klasy dataset dla PyTorch.
class ChatDataset(Dataset):
    def __init__(self):
        self.n_samples = len(x_train)
        self.x_data = x_train
        self.y_data = y_train

    def __getitem__(self, index):
        return self.x_data[index], self.y_data[index]

    def __len__(self):
        return self.n_samples

# Ustawienia parametrów modelu.
batch_size = 8
hidden_size = 8
output_size = len(tags)
input_size = len(x_train[0])
learning_rate = 0.001
num_epochs = 1000

# Inicjalizacja dataset i dataloader.
dataset = ChatDataset()
train_loader = DataLoader(dataset=dataset, batch_size=batch_size, shuffle=True, num_workers=0)

# Ustawienie urządzenia (GPU lub CPU).
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = Net(input_size, hidden_size, output_size)  # Inicjalizacja modelu.

criterion = nn.CrossEntropyLoss()  # Funkcja straty.
optimizer = torch.optim.Adam(model.parameters(), lr=learning_rate)  # Optymalizator.

# Pętla treningowa.
for epoch in range(num_epochs):
    for (words, labels) in train_loader:
        words = words.to(device)
        labels = labels.to(dtype=torch.long).to(device)

        outputs = model(words)
        loss = criterion(outputs, labels)

        optimizer.zero_grad()
        loss.backward()
        optimizer.step()

    if (epoch + 1) % 100 == 0:
        print(f"Epoch: {epoch + 1}/{num_epochs}, loss={loss.item():.4f}")

print(f"Final loss, loss={loss.item():.4f}")

# Zapisanie stanu modelu i innych parametrów do pliku.
data = {"model_state": model.state_dict(),
        "input_size": input_size,
        "hidden_size": hidden_size,
        "output_size": output_size,
        "list_of_words": list_of_words,
        "tags": tags}

FILE = "../data.pth"
torch.save(data, FILE)

print(f"Model saved to {FILE}")
