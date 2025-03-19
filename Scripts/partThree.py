import sqlite3
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from Scripts.query_database import fetch_country_data
import numpy as np
import matplotlib.pyplot as plt

def obtain_mu_hat(country):
    """Estimate the death rate μ_hat."""
    data = fetch_country_data(country)
    
    if not data:
        return None  # Handle missing data

    active, new_cases, _, _, _, new_deaths, _, _, _, _ = data
    active_cases = int(active) - int(new_cases)
    
    mu_hat = int(new_deaths) / active_cases if active_cases > 0 else 0
    return mu_hat


def obtain_alpha_hat(country):
    """Estimate the reinfection rate α_hat."""
    gamma_hat = 1 / 4.5  # Given in the assignment
    data = fetch_country_data(country)

    if not data:
        return None  

    active, new_cases, recovered, new_recovered, _, _, _, _, _, _ = data
    active_cases = int(active) - int(new_cases)
    recovered_cases = int(recovered) - int(new_recovered)

    alpha_hat = -(int(new_recovered) - gamma_hat * active_cases) / recovered_cases if recovered_cases > 0 else 0
    return alpha_hat


def obtain_beta_hat(country):
    """Estimate the transmission rate β_hat."""
    gamma_hat = 1 / 4.5  
    data = fetch_country_data(country)

    if not data:
        return None  

    active, new_cases, recovered, new_recovered, deaths, new_deaths, population, _, _, _ = data
    active_cases = int(active) - int(new_cases)
    recovered_cases = int(recovered) - int(new_recovered)
    death_cases = int(deaths) - int(new_deaths)
    susceptible_cases = population - (active_cases + recovered_cases + death_cases)
    
    alpha_hat = obtain_alpha_hat(country)
    delta_susceptible = -(new_cases + new_recovered + new_deaths)

    beta_hat = ((alpha_hat * recovered_cases - delta_susceptible) * (population / (susceptible_cases * active_cases))) if (susceptible_cases * active_cases) > 0 else 0
    return beta_hat




def produce_reproduction_number_trajectory(country, days):
    """Calculate and plot R0 trajectory for a given country over time."""
    alpha_hat = obtain_alpha_hat(country)
    beta_hat = obtain_beta_hat(country)
    gamma_hat = 1 / 4.5
    mu_hat = obtain_mu_hat(country)

    data = fetch_country_data(country)
    if not data:
        print("No data available for", country)
        return

    active, new_cases, recovered, new_recovered, deaths, new_deaths, population, _, _, _ = data
    susceptible_cases = population - (active + recovered + deaths)
    
    susceptible = [susceptible_cases]
    active_cases = [active]
    recovered_cases = [recovered]
    deaths_cases = [deaths]
    R0_values = []

    for _ in range(days):
        delta_S = alpha_hat * recovered_cases[-1] - beta_hat * susceptible[-1] * active_cases[-1] / population
        delta_I = beta_hat * susceptible[-1] * active_cases[-1] / population - mu_hat * active_cases[-1] - gamma_hat * active_cases[-1]
        delta_R = gamma_hat * active_cases[-1] - alpha_hat * recovered_cases[-1]
        delta_D = mu_hat * active_cases[-1]

        susceptible.append(susceptible[-1] + delta_S)
        active_cases.append(active_cases[-1] + delta_I)
        recovered_cases.append(recovered_cases[-1] + delta_R)
        deaths_cases.append(deaths_cases[-1] + delta_D)

        R0_values.append(beta_hat / gamma_hat)

    plt.figure(figsize=(12, 6))
    plt.plot(range(days), R0_values, label="R₀ over time", color="blue")
    plt.xlabel("Days")
    plt.ylabel("R₀")
    plt.title(f"Reproduction Number (R₀) Trajectory for {country}")
    plt.legend()
    plt.grid()
    plt.show()
