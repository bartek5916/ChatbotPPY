import torch  # Importowanie głównej biblioteki PyTorch
import torch.nn as nn  # Importowanie modułu sieci neuronowych z PyTorch

# Struktura sieci neuronowej
class Net(nn.Module):  # Definiowanie klasy 'Net', która dziedziczy po 'nn.Module'
    def __init__(self, input_size, hidden_size, output_size):  # Metoda konstruktor inicjalizująca sieć
        super(Net, self).__init__()  # Wywołanie konstruktora klasy nadrzędnej 'nn.Module'
        self.fc1 = nn.Linear(input_size, hidden_size)  # Definiowanie pierwszej w pełni połączonej warstwy z rozmiarem wejścia i warstwy ukrytej
        self.fc2 = nn.Linear(hidden_size, hidden_size)  # Definiowanie drugiej w pełni połączonej warstwy z rozmiarem warstwy ukrytej
        self.fc3 = nn.Linear(hidden_size, output_size)  # Definiowanie trzeciej w pełni połączonej warstwy z rozmiarem wyjścia
        self.relu = nn.ReLU()  # Definiowanie funkcji aktywacji ReLU

    def forward(self, x):  # Metoda definiująca przepływ danych w sieci (forward pass)
        out = self.fc1(x)  # Przesłanie danych wejściowych przez pierwszą warstwę
        out = self.relu(out)  # Zastosowanie funkcji aktywacji ReLU
        out = self.fc2(out)  # Przesłanie danych przez drugą warstwę
        out = self.relu(out)  # Ponowne zastosowanie funkcji aktywacji ReLU
        out = self.fc3(out)  # Przesłanie danych przez trzecią warstwę
        return out  # Zwrócenie wyniku
