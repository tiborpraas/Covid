import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.integrate import solve_ivp
import sqlite3
import plotly.express as px

# Connect to the database
db_file_path = "covid_database.db"
conn = sqlite3.connect(db_file_path)

# Load necessary tables using SQL queries for efficiency
df_csv = pd.read_csv("complete.csv")
df_country_wise = pd.read_sql_query("SELECT `Country.Region`, Confirmed, Deaths, Recovered, Active FROM country_wise", conn)
df_worldometer = pd.read_sql_query("SELECT `Country.Region`, Population FROM worldometer_data", conn)
df_usa_counties = pd.read_sql_query("SELECT Admin2, Province_State, Confirmed, Deaths FROM usa_county_wise", conn)

# Merge data
df_merged = pd.merge(df_csv, df_country_wise, on='Country.Region', how='left', suffixes=('_csv', '_db'))
df_final = pd.merge(df_merged, df_worldometer, on="Country.Region", how="left")

# Handle missing values
df_final.fillna(0, inplace=True)

# Convert Date column to datetime format
df_final["Date"] = pd.to_datetime(df_final["Date"])

# Estimate parameters dynamically with γ fixed at 1/4.5
df_final["New_deaths"] = df_final["Deaths_csv"].diff().fillna(0)
df_final["New_recovered"] = df_final["Recovered_csv"].diff().fillna(0)
df_final["New_cases"] = df_final["Confirmed_csv"].diff().fillna(0)

df_final["mu"] = df_final["New_deaths"] / df_final["Confirmed_csv"]
df_final["gamma"] = 1 / 4.5

df_final["beta"] = (df_final["New_cases"] / (df_final["Confirmed_csv"] * df_final["Population"])) * df_final["Population"]

df_final["mu"].fillna(method="ffill", inplace=True)
df_final["beta"].fillna(method="ffill", inplace=True)

df_final["R0"] = df_final["beta"] / df_final["gamma"]

# Function to get R0 for a given country
def get_R0_trajectory(country):
    country_data = df_final[df_final["Country.Region"] == country]
    plt.figure(figsize=(12, 6))
    plt.plot(country_data["Date"], country_data["R0"], label=f"R0 for {country}", color="purple")
    plt.xlabel("Date")
    plt.ylabel("R0 Value")
    plt.title(f"Estimated R0 Over Time for {country}")
    plt.axhline(y=1, color="r", linestyle="--", label="Threshold (R0 = 1)")
    plt.legend()
    plt.xticks(rotation=45)
    plt.grid()
    plt.show()

# Fixing Europe Map visualization
df_europe = df_final[df_final["WHO.Region"] == "Europe"]
fig = px.choropleth(df_europe, 
                    locations="Country.Region", 
                    locationmode="country names",
                    color="Active_csv",
                    hover_name="Country.Region",
                    title="Active COVID-19 Cases in Europe",
                    color_continuous_scale="Reds")
fig.show()

# Identify top 5 US counties with highest deaths and cases
df_usa_sorted_cases = df_usa_counties.sort_values(by="Confirmed", ascending=False).head(5)
df_usa_sorted_deaths = df_usa_counties.sort_values(by="Deaths", ascending=False).head(5)

# Plot top 5 counties
def plot_top_us_counties():
    plt.figure(figsize=(12, 6))
    plt.bar(df_usa_sorted_cases["Admin2"], df_usa_sorted_cases["Confirmed"], color="blue", label="Cases")
    plt.bar(df_usa_sorted_deaths["Admin2"], df_usa_sorted_deaths["Deaths"], color="red", label="Deaths")
    plt.xlabel("County")
    plt.ylabel("Count")
    plt.title("Top 5 US Counties with Most COVID-19 Cases and Deaths")
    plt.legend()
    plt.xticks(rotation=45)
    plt.grid()
    plt.show()

plot_top_us_counties()

# SIRD model
def SIRD_model(t, y, alpha, beta, gamma, mu, N):
    S, I, R, D = y
    dSdt = -beta * S * I / N + alpha * R
    dIdt = beta * S * I / N - gamma * I - mu * I
    dRdt = gamma * I - alpha * R
    dDdt = mu * I
    return [dSdt, dIdt, dRdt, dDdt]

first_day = df_final[df_final["Date"] == df_final["Date"].min()].iloc[0]
S0 = first_day["Population"] - first_day["Confirmed_csv"]
I0 = first_day["Confirmed_csv"]
R0 = first_day["Recovered_csv"]
D0 = first_day["Deaths_csv"]
N = first_day["Population"]

alpha = 0.01
beta = df_final["beta"].mean()
gamma = df_final["gamma"].mean()
mu = df_final["mu"].mean()

t_span = (0, 180)
t_eval = np.linspace(t_span[0], t_span[1], 180)

solution = solve_ivp(SIRD_model, t_span, [S0, I0, R0, D0], args=(alpha, beta, gamma, mu, N), t_eval=t_eval)

# Plot SIRD model results
plt.figure(figsize=(12, 6))
plt.plot(t_eval, solution.y[0], label="Susceptible (S)", linestyle="--", color="blue")
plt.plot(t_eval, solution.y[1], label="Infected (I)", linestyle="-", color="red")
plt.plot(t_eval, solution.y[2], label="Recovered (R)", linestyle=":", color="green")
plt.plot(t_eval, solution.y[3], label="Deceased (D)", linestyle="-.", color="black")
plt.xlabel("Days")
plt.ylabel("Population")
plt.title("SIRD Model Simulation Over 180 Days")
plt.legend()
plt.grid()
plt.show()
