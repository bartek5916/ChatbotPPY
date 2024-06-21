import re
from datetime import datetime, timedelta
import pyodbc

class ShippingManager:
    def __init__(self):
        # Inicjalizacja połączenia z bazą danych przy użyciu ODBC
        self.conn = pyodbc.connect(
            'DRIVER={ODBC Driver 18 for SQL Server};'
            f'SERVER=(localdb)\\MyDB2;'
            f'DATABASE=master;'
        )
        self.conn.autocommit = True

    def get_shipment_by_id(self, shipment_number):
        # Pobranie szczegółów przesyłki na podstawie jej numeru
        cursor = self.conn.cursor()
        query = '''
        SELECT 
            p.Id as Id,
            kurier.Imie + ' ' + kurier.Nazwisko as Kurier, 
            magazynier.Imie + ' ' + magazynier.Nazwisko as Magazynier, 
            nadawca.Imie + ' ' + nadawca.Nazwisko as Nadawca, 
            odbiorca.Imie + ' ' + odbiorca.Nazwisko as Odbiorca, 
            p.Id_Paczka, 
            p.Data_Nadania, 
            p.Przewidywana_Data_Odbioru, 
            p.Status
        FROM Przesylka p
        JOIN Osoba kurier ON p.Id_Kurier = kurier.Id
        JOIN Osoba magazynier ON p.Id_Magazynier = magazynier.Id
        JOIN Osoba nadawca ON p.Id_Klient_Nadawca = nadawca.Id
        JOIN Osoba odbiorca ON p.Id_Klient_Odbiorca = odbiorca.Id
        WHERE p.Nr_przesylki = ?
        '''
        cursor.execute(query, (shipment_number,))
        row = cursor.fetchone()
        if row:
            # Formatowanie wyników zapytania do czytelnej postaci
            formatted_result = f"ID Przesyłki: {row.Id}, Kurier: {row.Kurier}, Magazynier: {row.Magazynier}, Nadawca: {row.Nadawca}, Odbiorca: {row.Odbiorca}, ID Paczki: {row.Id_Paczka}, Data Nadania: {row.Data_Nadania}, Data Dostarczenia: {row.Przewidywana_Data_Odbioru}, Status: {row.Status}"
            return formatted_result
        return "Przesyłka o podanym ID nie została znaleziona."

    def get_pickup_points_excluding_home(self):
        # Pobranie punktów odbioru/nadania, z wyłączeniem tych znajdujących się w domu
        cursor = self.conn.cursor()
        query = '''
        SELECT Nazwa, Adres, Nr_telefonu, Godziny_otwarcia, Obiekt 
        FROM PunktOdbioruNadania
        WHERE Obiekt != 'Dom'
        '''
        cursor.execute(query)
        results = cursor.fetchall()
        formatted_results = []
        for point in results:
            formatted_result = f"Nazwa: {point[0]}, Adres: {point[1]}, Nr telefonu: {point[2]}, Godziny otwarcia: {point[3]}, Obiekt: {point[4]}"
            formatted_results.append(formatted_result)
        return "\n".join(formatted_results)

    def update_delivery_location(self, shipment_id, new_location):
        # Aktualizacja miejsca dostawy dla danej przesyłki
        cursor = self.conn.cursor()
        query = '''
        UPDATE Przesylka
        SET Miejsce_dostawy = ?
        WHERE Id = ?
        '''
        cursor.execute(query, (new_location, shipment_id))
        self.conn.commit()
        return f"Miejsce dostawy przesyłki o ID {shipment_id} zostało zaktualizowane do: {new_location}"

    def update_delivery_date(self, shipment_number):
        # Aktualizacja daty dostawy przesyłki na podstawie numeru przesyłki
        cursor = self.conn.cursor()

        # Definiowanie wzorca za pomocą wyrażenia regularnego
        wzorzec = r'^PL\d{4}/SK, (\d{4}), (\d{2}), (\d{2})$'

        # Sprawdzenie czy shipment_number pasuje do wzorca
        match = re.match(wzorzec, shipment_number)
        final_shipment_number = match.group(0).split(",")[0]
        if match:
            # Wyciągnięcie roku, miesiąca i dnia z shipment_number
            year, month, day = match.groups()
            new_delivery_date = datetime(int(year), int(month), int(day))

            # Obliczenie nowej daty dostarczenia (przynajmniej 2 dni później niż data nadania)
            new_delivery_date = new_delivery_date.strftime('%Y-%m-%d')

            # Aktualizacja daty dostarczenia
            query = '''
            UPDATE Przesylka
            SET Przewidywana_Data_Odbioru = ?
            WHERE Nr_przesylki = ?
            '''
            cursor.execute(query, (new_delivery_date, final_shipment_number))
            self.conn.commit()
            return f"Data dostarczenia przesyłki o numerze: {final_shipment_number} została zaktualizowana do: {new_delivery_date}"
        else:
            return f"Przesyłka o numerze: {final_shipment_number} nie została znaleziona lub ma niepoprawny format."

    def __del__(self):
        # Zamknięcie połączenia z bazą danych przy usuwaniu obiektu
        self.conn.close()
