import sqlite3

# Stap 1: Maak verbinding met de database
# Vervang 'covid_database.db' door het pad naar je databasebestand
connection = sqlite3.connect("Data/covid_database.db")

# Stap 2: Maak een cursor-object om SQL-query's uit te voeren
cursor = connection.cursor()

# Stap 3: Schrijf en voer een SQL-query uit
# Voorbeeld: Selecteer de eerste 10 rijen uit een tabel genaamd 'cases'
query = "SELECT * FROM country_wise LIMIT 10;"
cursor.execute(query)

# Stap 4: Haal de resultaten op
results = cursor.fetchall()

# Stap 5: Print de resultaten
for row in results:
    print(row)

# Stap 6: Sluit de verbinding
connection.close()