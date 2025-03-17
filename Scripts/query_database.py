import sqlite3
def fetch_country_data(country):
    """Fetch relevant COVID-19 data for a given country from the database."""
    connection = sqlite3.connect("Data/covid_database.db")
    cursor = connection.cursor()

    query = """
    SELECT cw.[Active], cw.[New.cases], cw.[Recovered], cw.[New.recovered], cw.[Deaths], cw.[New.deaths],
           wd.[Population], wd.[ActiveCases], wd.[TotalDeaths], wd.[TotalRecovered]
    FROM country_wise cw
    JOIN worldometer_data wd ON cw.[Country.Region] = wd.[Country.Region]
    WHERE cw.[Country.Region] = ?;
    """
    cursor.execute(query, (country,))
    result = cursor.fetchone()
    
    connection.close()
    
    return result  # Returns a tuple with all necessary values

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