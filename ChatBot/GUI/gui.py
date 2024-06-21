import tkinter as tk
from tkinter import ttk
from tkinter import scrolledtext
from ModelHandler.chat import ChatBot

# Definiowanie zmiennej globalnej do śledzenia, czy czekamy na numer przesyłki
waiting_for_package_number = False


def send_message(event=None):
    global waiting_for_package_number  # Deklaracja zmiennej globalnej
    global waiting_for_new_date
    global tag_status
    chat = ChatBot()
    user_message = user_input.get()

    if user_message:
        chat_window.config(state=tk.NORMAL)
        chat_window.insert(tk.END, "Ty: " + user_message + '\n', "user")

        # Sprawdzenie, czy czekamy na numer przesyłki
        if not waiting_for_package_number:
            response = chat.get_response(user_message)

            if isinstance(response, list):
                chat_window.insert(tk.END, "Szczepan: " + response[1], "bot")

                if chat.check_for_word_date(response[1]):
                    chat_window.insert(tk.END,
                                       "Szczepan: Podaj numer przesyłki i nową datę dostawy w formacie PLxxxx/SK, rok, miesiąc, dzień lub wpisz 'wyjdź' aby anulować operację: " + "\n",
                                       "bot")
                    waiting_for_package_number = True
                    tag_status = response[0]
                elif chat.check_for_word_number(response[1]):
                    chat_window.insert(tk.END,
                                       "Szczepan: Podaj numer przesyłki w formacie PLxxxx/SK lub wpisz 'wyjdź' aby anulować operację: " + "\n",
                                       "bot")
                    waiting_for_package_number = True
                    tag_status = response[0]
                elif chat.check_for_word_points(response[1]):
                    response = chat.get_pickup_points()
                    chat_window.insert(tk.END, '\n' + response + '\n', "bot")
            else:
                chat_window.insert(tk.END, "Szczepan: " + response, "bot")

        else:
            response = chat.check_shipment_number(user_message, tag_status)
            chat_window.insert(tk.END, "Szczepan: " + response + '\n', "bot")

            if response == "Numer przesyłki jest poprawny" or user_message.lower() == "wyjdź":
                waiting_for_package_number = False

        chat_window.config(state=tk.DISABLED)
        user_input.set("")
        entry_box.focus()


root = tk.Tk()
root.title("Szczepan - Kurierex")
root.geometry("500x600")
root.configure(bg='#483D8B')

# Konfiguracja stylu
style = ttk.Style()
style.theme_use("clam")

style.configure('TFrame', background='#483D8B')
style.configure('TLabel', background='#FFC0CB', foreground='#ffffff', font=('Helvetica', 12), padding=10)
style.configure('TButton', background='#89f076', foreground='#483D8B', font=('Helvetica', 12), padding=10)
style.configure('TEntry', font=('Helvetica', 12))

# Okno czatu
chat_frame = ttk.Frame(root)
chat_frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

chat_window = scrolledtext.ScrolledText(chat_frame, wrap=tk.WORD, state=tk.DISABLED, bg='#89f076', fg='#ffffff',
                                        font=('Verdana', 12), padx=10, pady=10)
chat_window.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
chat_window.tag_configure("user", foreground="#483D8B")
chat_window.tag_configure("bot", foreground="#DC143C")

# Ramka do wprowadzania tekstu
input_frame = ttk.Frame(root)
input_frame.pack(fill=tk.X, padx=10, pady=10)

user_input = tk.StringVar()
user_input2 = tk.StringVar()

# Pole wprowadzania tekstu
entry_box = ttk.Entry(input_frame, textvariable=user_input, font=('Helvetica', 12))
entry_box.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10), pady=10)
entry_box.bind("<Return>", send_message)

# Przycisk wysyłania
send_button = ttk.Button(input_frame, text="Wyślij", command=send_message)
send_button.pack(side=tk.RIGHT, pady=10)

root.mainloop()