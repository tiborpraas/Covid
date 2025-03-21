import sqlite3
import pandas as pd

def mapping_datasets(cursor):
    query = """
    CREATE TABLE IF NOT EXISTS data_mapping (
        country_wise_name VARCHAR(255),
        worldometer_name VARCHAR(255)
    );
    """
    cursor.execute(query)

    
    country_mapping = [
    ('Brunei', 'Brunei '),
    ('Burma', 'Myanmar'),
    ('Central African Republic', 'CAR'),
    ('Congo (Kinshasa)', 'Congo'),
    ('Congo (Brazzaville)', 'DRC'),
    ("Cote d'Ivoire", "Ivory Coast"),
    ('Holy See', 'Vatican City'),
    ('Saint Vincent and the Grenadines', 'St. Vincent Grenadines'),
    ('South Korea', 'S. Korea'),
    ('Taiwan*', 'Taiwan'),
    ('US', 'USA'),
    ('United Arab Emirates', 'UAE'),
    ('United Kingdom', 'UK'),
    ('West Bank and Gaza', 'Palestine'),
    ]

    WHO_Region_Mapping = [
        ('Eastern Mediterranean', 'EasternMediterranean'),
        ('Western Pacific', 'WesternPacific'),
        ('South-East Asia', 'South-EastAsia'),
    ]

    for country_wise_name, worldometer_name in country_mapping:
        query = """
        INSERT INTO country_mapping (country_wise_name, worldometer_name)
        VALUES (?, ?);
        """
        cursor.execute(query, (country_wise_name, worldometer_name))

    return



def fetch_country_data(country):
    """Fetch relevant COVID-19 data for a given country from the database."""
    connection = sqlite3.connect("Data/covid_database.db")
    cursor = connection.cursor()

    # Try looking up the value without the use of mapping
    query = """
    SELECT cw.[Active], cw.[New.cases], cw.[Recovered], cw.[New.recovered], cw.[Deaths], cw.[New.deaths],
           wd.[Population], wd.[ActiveCases], wd.[TotalDeaths], wd.[TotalRecovered]
    FROM country_wise cw
    JOIN worldometer_data wd ON cw.[Country.Region] = wd.[Country.Region]
    WHERE cw.[Country.Region] = ?;
    """
    cursor.execute(query, (country,))
    result = cursor.fetchone()

    # Check if the name corresponds to a name in the country_wise or worldometer dataset 
    if not result:
         mapping_datasets(cursor)
         mapping_list = ()


         query = "SELECT [worldometer_name] FROM country_mapping WHERE [country_wise_name] = ?;"

         cursor.execute(query, (country,))
         queryResult = cursor.fetchone()
         if queryResult: 
            mapping_list = (country, str(queryResult[0]))

         if not mapping_list:
            query = "SELECT [country_wise_name] FROM country_mapping WHERE [worldometer_name] = ?;"
            cursor.execute(query, (country,))
            queryResult = cursor.fetchone()
            if queryResult:
                mapping_list = (str(queryResult[0]), country)

         if mapping_list: # Lookup values with the help of the names in both datasets
            mapped_country = str(mapping_list[0])

            query = """
            SELECT cw.[Active], cw.[New.cases], cw.[Recovered], cw.[New.recovered], cw.[Deaths], cw.[New.deaths],
            wd.[Population], wd.[ActiveCases], wd.[TotalDeaths], wd.[TotalRecovered]
            FROM country_wise cw
            JOIN country_mapping cm ON cw.[Country.Region] = cm.country_wise_name
            JOIN worldometer_data wd ON cm.worldometer_name = wd.[Country.Region]
            WHERE cw.[Country.Region] = ?;
            """
            cursor.execute(query, (mapped_country,))
            result = cursor.fetchone()

    connection.close()

    return result  # Returns a tuple with all necessary values or None if not found

def date_ranges(cursor):
    query = """
    SELECT DATE(MIN(date)) AS min_date, DATE(MAX(date)) AS max_date
    FROM complete_data;
    """

    cursor.execute(query)

    result = cursor.fetchone()

    return result

def Country_Population(cursor, country):
    # China and Kosovo data does not exist in the worldometer dataset, the population in 2020 was gathered from worldbank.org
    if country == "China":
        return 1411100000 # From worldbank.org
    
    if country == "Kosovo":
        return 1790152 # From worldbank.org

    query = """
    SELECT [Population] 
    FROM worldometer_data 
    WHERE [Country.Region] = ?
    """

    cursor.execute(query, (country,))

    result = cursor.fetchone()
    if result: 
        return int(result[0])

    if not result:
        mapping_datasets(cursor)
        mapping_list = ()

        query = """
        SELECT [worldometer_name] 
        FROM country_mapping 
        WHERE [country_wise_name] = ?;
        """

        cursor.execute(query, (country,))
        queryResult = cursor.fetchone()
        if queryResult: 
            mapping_list = (country, str(queryResult[0]))

        if not mapping_list:
            query = "SELECT [country_wise_name] FROM country_mapping WHERE [worldometer_name] = ?;"
            cursor.execute(query, (country,))
            queryResult = cursor.fetchone()
            if queryResult:
                mapping_list = (str(queryResult[0]), country)

        if mapping_list:
            query = """
            SELECT [Population] 
            FROM worldometer_data 
             WHERE [Country.Region] = ?
             """

            cursor.execute(query, (mapping_list[1],))

            result = cursor.fetchone()
            return int(result[0])
    
    return None

def Total_Cases_Per_Day_Global(connection, startdate, enddate):
    query = """
    SELECT date,
           SUM(Confirmed) AS Total_Confirmed_Cases,
           SUM(Deaths) AS Total_Deaths,
           SUM(Recovered) AS Total_Recovered,
           SUM(Active) AS Total_Active_Cases
    FROM complete_data
    WHERE date BETWEEN ? AND ?
    GROUP BY date
    ORDER BY date;
    """

    df = pd.read_sql(query, connection, params=(startdate, enddate))

    cursor = connection.cursor()

    query = """
    SELECT DISTINCT [Country.Region]
    FROM complete_data
    """

    cursor.execute(query)

    result = cursor.fetchall()

    population = 0

    for country in result:
        population += Country_Population(cursor, country[0])

    df['Population'] = population

    return df

def Total_Cases_Per_Day_Continental(connection, continent, startdate, enddate):
    query = """
    SELECT date,
           SUM(Confirmed) AS Total_Confirmed_Cases,
           SUM(Deaths) AS Total_Deaths,
           SUM(Recovered) AS Total_Recovered,
           SUM(Active) AS Total_Active_Cases
    FROM complete_data
    WHERE [WHO.Region] = ? AND date BETWEEN ? AND ?
    GROUP BY date
    ORDER BY date;
    """

    df = pd.read_sql(query, connection, params=(continent, startdate, enddate))

    cursor = connection.cursor()

    query = """
    SELECT DISTINCT [Country.Region]
    FROM complete_data
    WHERE [WHO.Region] = ? 
    """

    cursor.execute(query, (continent,))

    result = cursor.fetchall()

    population = 0

    for country in result:
        population += Country_Population(cursor, country[0])

    df['Population'] = population
    
    return df

def Total_Cases_Per_Day_Country(connection, continent, country, startdate, enddate):
    query = """
    SELECT date,
           SUM(Confirmed) AS Total_Confirmed_Cases,
           SUM(Deaths) AS Total_Deaths,
           SUM(Recovered) AS Total_Recovered,
           SUM(Active) AS Total_Active_Cases
    FROM complete_data
    WHERE [WHO.Region] = ? AND [Country.Region] = ? AND date BETWEEN ? AND ?
    GROUP BY date
    ORDER BY date;
    """

    df = pd.read_sql(query, connection, params=(continent, country, startdate, enddate))
    df['Population'] = Country_Population(connection.cursor(), country)

    return df

def Total_Cases_Per_Day_Province(connection, continent, country, province, startdate, enddate):
    query = """
    SELECT date,
           SUM(Confirmed) AS Total_Confirmed_Cases,
           SUM(Deaths) AS Total_Deaths,
           SUM(Recovered) AS Total_Recovered,
           SUM(Active) AS Total_Active_Cases
    FROM complete_data
    WHERE [WHO.Region] = ? AND [Country.Region] = ?  AND [Province.State] = ? AND date BETWEEN ? AND ?
    GROUP BY date
    ORDER BY date;
    """

    df = pd.read_sql(query, connection, params=(continent, country, province, startdate, enddate))

    return df







