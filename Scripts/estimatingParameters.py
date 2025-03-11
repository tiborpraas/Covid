import sqlite3
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import numpy as np

def obtain_mu_hat(country):
    connection = sqlite3.connect("Data/covid_database.db")
    cursor = connection.cursor()

    query = "SELECT [Active], [New.deaths], [New.cases] FROM country_wise WHERE [Country.Region] = ?;"
    cursor.execute(query, (country,))
    result = cursor.fetchone()
    active = int(result[0]) - int(result[2])
    new_deaths = int(result[1])

    connection.close()

    mu_hat = new_deaths / active

    return mu_hat

def obtain_alpha_hat(country):
    # Given in the assignment
    gamma_hat = 1 / 4.5

    connection = sqlite3.connect("Data/covid_database.db")
    cursor = connection.cursor()

    query = "SELECT [Active], [New.cases], [Recovered], [New.recovered] FROM country_wise WHERE [Country.Region] = ?;"
    cursor.execute(query, (country,))
    result = cursor.fetchone()
    active = int(result[0]) - int(result[1])
    recovered = int(result[2]) - int(result[3])
    new_recovered = int(result[3])

    connection.close()

    alpha_hat = -(new_recovered - gamma_hat * active) / recovered

    return alpha_hat

def obtain_beta_hat(country):
    # Given in the assignment
    gamma_hat = 1 / 4.5

    connection = sqlite3.connect("Data/covid_database.db")
    cursor = connection.cursor()

    query = "SELECT [Active], [New.cases], [Recovered], [New.recovered], [Deaths], [New.deaths] FROM country_wise WHERE [Country.Region] = ?;"
    cursor.execute(query, (country,))
    result = cursor.fetchone()
    active = int(result[0]) - int(result[1])
    recovered = int(result[2]) - int(result[3])
    death = int(result[4]) - int(result[5])
    delta_susceptible = -(result[1] + result[3] + result[5])

    query = "SELECT [Population], [ActiveCases], [TotalDeaths], [TotalRecovered] FROM worldometer_data WHERE [Country.Region] = ?;"
    cursor.execute(query, (country,))
    result = cursor.fetchone()
    population = int(result[0])
    susceptible = int(result[0]) - int(result[1]) - int(result[2]) - int(result[3])

    connection.close()
    alpha_hat = obtain_alpha_hat(country)
    beta_hat = (alpha_hat * recovered - delta_susceptible) * (population / (susceptible * active)) 
    

    return beta_hat

def Produce_reproduction_number_trajectory(country, length):
    #Initial estimators for R0:
    alpha_hat = obtain_alpha_hat(country)
    beta_hat = obtain_beta_hat(country)
    gamma_hat = 1 / 4.5 # Given in the assignment
    mu_hat = obtain_mu_hat(country)

    alpha_hat = 0.01
    beta_hat = 0.3
    gamma_hat = 0.1
    mu_hat = 0.01

    connection = sqlite3.connect("Data/covid_database.db")
    cursor = connection.cursor()
    
    # Lookup active cases, recovered and deaths
    query = "SELECT [Active], [New.cases], [Recovered], [New.recovered], [Deaths], [New.deaths] FROM country_wise WHERE [Country.Region] = ?;"
    cursor.execute(query, (country,))
    result = cursor.fetchone()
    active_day0 = int(result[0]) - int(result[1])
    recovered_day0 = int(result[2]) - int(result[3])
    death_day0 = int(result[4]) - int(result[5])
    
    # Lookup population and amount of susceptible people at the start
    query = "SELECT [Population], [ActiveCases], [TotalDeaths], [TotalRecovered] FROM worldometer_data WHERE [Country.Region] = ?;"
    cursor.execute(query, (country,))
    result = cursor.fetchone()
    susceptible_day0 = int(result[0]) - int(result[1]) - int(result[2]) - int(result[3])
    susceptible_day0 = 17000000
    population = int(result[0])
    population = susceptible_day0 + active_day0 + death_day0 + recovered_day0    

    connection.close()

    # SIR model
    susceptible = [susceptible_day0]
    active_cases = [active_day0]
    recovered = [recovered_day0]
    deaths = [death_day0]
    Reproduction_number = []

    for i in range(length):
        delta_Susceptible = round(alpha_hat * recovered[-1] - beta_hat * susceptible[-1] * active_cases[-1] / population)
        delta_Active = round(beta_hat * susceptible[-1] * active_cases[-1] / population - mu_hat * active_cases[-1] - gamma_hat * active_cases[-1])
        delta_Recovered = round(gamma_hat * active_cases[-1] - alpha_hat * recovered[-1])
        delta_Death = round(mu_hat * active_cases[-1])

        mu_hat = delta_Death / active_cases[-1]
        alpha_hat = (gamma_hat * active_cases[-1] - delta_Recovered) / recovered[-1]
        beta_hat = (alpha_hat * recovered[-1] - delta_Susceptible) * (population / (susceptible[-1] * active_cases[-1])) 

        # Track reproduction_number over time
        Reproduction_number.append(beta_hat/gamma_hat)

        susceptible.append(susceptible[-1] + delta_Susceptible)
        active_cases.append(active_cases[-1] + delta_Active)
        recovered.append(recovered[-1] + delta_Recovered)
        deaths.append(deaths[-1] + delta_Death)


    days_list = list(range(length))

    tick_positions = np.linspace(0, length - 1, 10, dtype=int)
    tick_labels = [str(day) for day in tick_positions] 

    plt.figure(figsize=(12, 6))
    plt.plot(days_list, Reproduction_number, marker='o', linestyle='-', color='b', label=r"$R_0$")

    plt.xlabel("Days passed")
    plt.ylabel("Reproduction number")
    plt.title(f"Reproduction number over time of {country}")
    plt.xticks(tick_positions, rotation=45)
    plt.grid(True)
    plt.legend()

    plt.show()

    return

Produce_reproduction_number_trajectory('France', 1000)