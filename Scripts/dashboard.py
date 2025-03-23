import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import sqlite3
from scipy.optimize import minimize
import matplotlib.dates as mdates
import plotly.express as px
import createDataFrame
from partFour import plot_visualization_map_WHO_Region

# Load data
@st.cache_data
def load_data():
    df_complete = pd.read_csv("../Data/complete.csv", parse_dates=["Date"])
    df_complete[["Confirmed", "Deaths", "Recovered", "Active"]] = df_complete[["Confirmed", "Deaths", "Recovered", "Active"]].fillna(0)
    
    # Keep only 1 row from rows that have the same WHO.Region, Country.Region, Province.State and Date as another
    df_complete.drop_duplicates(["WHO.Region", "Country.Region", "Province.State", "Date"], inplace=True)

    

    # Load day-wise data
    df_day = pd.read_csv("Data/day_wise.csv")
    df_day["Date"] = pd.to_datetime(df_day["Date"])
    df_day["Date"] = df_day["Date"].astype(str)  # Convert Date to string

    # Load country-wise data
    connection = sqlite3.connect("Data/covid_database.db")
    df_country = pd.read_sql_query("SELECT * FROM country_wise", connection)
    df_worldometer = pd.read_sql_query("SELECT * FROM worldometer_data", connection)
    df_usa_counties = pd.read_sql_query("SELECT * FROM usa_county_wise", connection)

    # Adds the complete.csv as a new table to the sql database without duplicates
    df_complete.to_sql("complete_data", connection, if_exists="replace", index=False)

    connection.close()

    return df_day, df_country, df_worldometer, df_usa_counties, df_complete

df_day, df_country, df_worldometer, df_usa_counties, df_complete = load_data()

# Title and description
st.title("COVID-19 Dashboard")
st.write("This dashboard provides insights into the spread of COVID-19 using data analysis and the SIR model.")

# Sidebar for user input
with st.sidebar:
    st.header("Filters")
    start_date = st.date_input("Start Date", pd.to_datetime(df_day["Date"].min()))
    end_date = st.date_input("End Date", pd.to_datetime(df_day["Date"].max()))
    selected_continent = st.sidebar.selectbox("Select Continent", [""] + list(df_complete["WHO.Region"].unique()), index=0)
    filtered_countries = df_complete[df_complete["WHO.Region"] == selected_continent]["Country.Region"].unique()

    selected_country = st.sidebar.selectbox("Select Country", [""] + list(filtered_countries))
    filtered_provinces = df_complete[df_complete["Country.Region"] == selected_country]["Province.State"].unique()

    if len(filtered_provinces) > 0:
        # Province Selection
        selected_province = st.sidebar.selectbox("Select Province", [""] + filtered_provinces)
    elif selected_country:
        st.write(f"No provinces available for {selected_country}")
        selected_province = None
    else: 
        st.write(f"No provinces available")
        selected_province = None
    

# Convert dates to datetime
start_date = pd.to_datetime(start_date)
end_date = pd.to_datetime(end_date)

# Filter data based on date range
filtered_df = df_day[(pd.to_datetime(df_day["Date"]) >= start_date) & (pd.to_datetime(df_day["Date"]) <= end_date)]

# Organize dashboard into tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs(["General Results", "SIR Model", "Data by location", "Top US Counties", "Case Fatality Rate"])

# General Results Tab
with tab1:
    st.header("General Results")
    st.write("### COVID-19 Time Series")

    st.write("#### Summary Statistics")
    summary_stats = filtered_df[["New cases", "Deaths", "Recovered"]].describe().T
    st.write(summary_stats)

    # Part 1 Graphs: New Cases, Deaths, Recovered Cases
    st.write("#### New Cases Over Time")
    fig1, ax1 = plt.subplots(figsize=(10, 4))
    ax1.plot(pd.to_datetime(filtered_df["Date"]), filtered_df["New cases"], color="blue", label="New Cases")
    ax1.set_xlabel("Date")
    ax1.set_ylabel("New Cases")
    ax1.legend()
    st.pyplot(fig1)

    st.write("#### Deaths Over Time")
    fig2, ax2 = plt.subplots(figsize=(10, 4))
    ax2.plot(pd.to_datetime(filtered_df["Date"]), filtered_df["Deaths"], color="red", label="Deaths")
    ax2.set_xlabel("Date")
    ax2.set_ylabel("Deaths")
    ax2.legend()
    st.pyplot(fig2)

    st.write("#### Recovered Cases Over Time")
    fig3, ax3 = plt.subplots(figsize=(10, 4))
    ax3.plot(pd.to_datetime(filtered_df["Date"]), filtered_df["Recovered"], color="green", label="Recovered")
    ax3.set_xlabel("Date")
    ax3.set_ylabel("Recovered Cases")
    ax3.legend()
    st.pyplot(fig3)

    # Continent-wise comparison
    st.write("#### COVID-19 Evolution Across Continents")
    continent_data = df_worldometer.groupby("Continent")[["TotalCases", "TotalDeaths", "TotalRecovered", "Population"]].sum().reset_index()

    million = 1000000
    continent_data["Cases_per_million"] = continent_data["TotalCases"] * million / continent_data["Population"]
    continent_data["Deaths_per_million"] = continent_data["TotalDeaths"] * million / continent_data["Population"]
    continent_data["Recovered_per_million"] = continent_data["TotalRecovered"] * million / continent_data["Population"]

    show_cases_per_million = st.checkbox("Display cases per million")

    if show_cases_per_million:
        # Plot the scaled data
        fig4 = px.bar(continent_data, 
                    x="Continent", 
                    y=["Cases_per_million", "Recovered_per_million", "Deaths_per_million"], 
                    title="Total Cases, Deaths, and Recovered per Population by Continent", 
                    barmode="group")

        st.plotly_chart(fig4)
    else:
        # Normal values, not scaled data
        fig4 = px.bar(continent_data, x="Continent", y=["TotalCases", "TotalRecovered", "TotalDeaths"], 
                 title="Total Cases, Deaths, and Recovered by Continent", barmode="group")
    st.plotly_chart(fig4)
    

    if selected_continent:
        st.write(f"#### Active cases across {selected_continent}")
        fig5 = plot_visualization_map_WHO_Region(selected_continent)
        st.plotly_chart(fig5)
    else:
        st.write(f"#### In order to display cases across a region, please select one")

# SIR Model Tab
with tab2:
    st.header("SIR Model Simulation")
    st.write("### SIR Model with Deaths")

    # Initial values
    S0 = 17000000
    I0 = df_day.loc[0, "Active"]
    R0 = df_day.loc[0, "Recovered"]
    D0 = df_day.loc[0, "Deaths"]
    N = S0 + I0 + R0 + D0

    # Parameters
    alpha = 0.01
    beta = 0.3
    gamma = 0.1
    mu = 0.01

    # Simulate SIR model
    S, I, R, D = [S0], [I0], [R0], [D0]
    for t in range(1, len(df_day)):
        delta_S = alpha * R[-1] - beta * S[-1] * I[-1] / N
        delta_I = beta * S[-1] * I[-1] / N - mu * I[-1] - gamma * I[-1]
        delta_R = gamma * I[-1] - alpha * R[-1]
        delta_D = mu * I[-1]
        
        S.append(S[-1] + delta_S)
        I.append(I[-1] + delta_I)
        R.append(R[-1] + delta_R)
        D.append(D[-1] + delta_D)

    # Plot SIR model
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(pd.to_datetime(df_day["Date"]), S, label="Susceptible")
    ax.plot(pd.to_datetime(df_day["Date"]), I, label="Infected")
    ax.plot(pd.to_datetime(df_day["Date"]), R, label="Recovered")
    ax.plot(pd.to_datetime(df_day["Date"]), D, label="Deceased")
    ax.set_xlabel("Date")
    ax.set_ylabel("Number of Individuals")
    ax.set_title("SIR Model with Deaths")
    ax.legend()
    st.pyplot(fig)

    # SIR Model Accuracy
    st.write("#### SIR Model vs Actual Data")
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(pd.to_datetime(df_day["Date"]), I, label="SIR Model (Infected)")
    ax.plot(pd.to_datetime(df_day["Date"]), df_day["Active"], label="Actual Active Cases")
    ax.set_xlabel("Date")
    ax.set_ylabel("Count")
    ax.set_title("SIR Model vs Actual Data")
    ax.legend()
    st.pyplot(fig)

    # Parameter Estimation
    st.write("#### Parameter Estimation")
    def error_function(params):
        beta, gamma = params
        if beta <= 0 or gamma <= 0:  # Ensure positive values
            return np.inf  # Return a large value for invalid parameters

        I_pred = [I0]
        for t in range(1, len(df_day)):
            delta_I = beta * S[t-1] * I_pred[t-1] / N - gamma * I_pred[t-1]
            I_pred.append(I_pred[t-1] + delta_I)
        return np.sum((np.array(I_pred) - df_day["Active"])**2)

    initial_guess = [0.3, 0.1]
    bounds = [(0.001, 10), (0.001, 10)]  # Ensure beta and gamma are positive
    result = minimize(error_function, initial_guess, bounds=bounds)

    if result.success:
        beta_est, gamma_est = result.x
        R0_est = beta_est / gamma_est
        st.write(f"Estimated beta: {beta_est:.2f}")
        st.write(f"Estimated gamma: {gamma_est:.2f}")
        st.write(f"Estimated R0: {R0_est:.2f}")
    else:
        st.error("Optimization failed. Check the data and parameters.")

# Country-Specific Data Tab
with tab3:
    st.header("Country-Specific Statistics")

    if selected_province:
        st.write(f"#### COVID-19 Data for {selected_province}")
    elif selected_country:
        st.write(f"#### COVID-19 Data for {selected_country}")
    elif selected_continent:
        st.write(f"#### COVID-19 Data for {selected_continent}")
    else:
        st.write("### Global COVID-19 Data")

    df = createDataFrame.createDataFrameOverTime(selected_continent, selected_country, selected_province, start_date, end_date)
    df["Date"] = pd.to_datetime(df["Date"])
    df["Mortality Rate (%)"] = df["Total_Deaths"] * 100 / df["Total_Confirmed_Cases"]

    # Filter data for selected country
    max_value = df["Total_Confirmed_Cases"].max()
    df_data = df[df["Total_Confirmed_Cases"] == max_value]
    # df_data["Date"]

    st.write(df_data)

    if not selected_province:
        show_per_million = st.checkbox("Show cases per million")
    else:
        show_per_million = False # No data available if province is selected so option should not be available

    if show_per_million:
        if selected_country:
            st.write(f"#### COVID-19 over time for {selected_country} in cases per million")
        elif selected_continent:
            st.write(f"#### COVID-19 over time for {selected_continent} in cases per million")
        else:
            st.write("#### Global COVID-19 spread over time in cases per million")

        df_population = createDataFrame.dataFrameToCasesPerMillion(df)
        fig1, ax1 = plt.subplots(figsize=((10,6)))
        ax1.plot(df_population["Date"], df_population["Total_Active_Cases"], label="Active Cases", color="blue")
        ax1.plot(df_population["Date"], df_population["Total_Recovered"], label="Recovered", color="green")
        ax1.plot(df_population["Date"], df_population["Total_Deaths"], label="Deaths", color="red")

        ax1.set_xlabel("Date")
        ax1.xaxis.set_major_locator(mdates.MonthLocator(interval=1))
        ax1.set_ylabel("Cases")
        ax1.legend()
        st.pyplot(fig1) # Plot selected country, continent or global for cases per million
    else:
        if selected_province:
            st.write(f"#### Covid-19 over time for {selected_province}")
        elif selected_country:
            st.write(f"#### Covid-19 over time for {selected_country}")
        elif selected_continent:
            st.write(f"#### Covid-19 over time for {selected_continent}")
        else:
            st.write("#### Global COVID-19 spread over time")
    
        fig2, ax2 = plt.subplots(figsize=(10,6))
        ax2.plot(df["Date"], df["Total_Active_Cases"], label="Active Cases", color="blue")
        ax2.plot(df["Date"], df["Total_Recovered"], label="Recovered", color="green")
        ax2.plot(df["Date"], df["Total_Deaths"], label="Deaths", color="red")

        ax2.set_xlabel("Date")
        ax2.xaxis.set_major_locator(mdates.MonthLocator(interval=1))
        ax2.set_ylabel("Cases")
        ax2.legend()

        st.pyplot(fig2) # Plot the total number of cases for the selected province
        

    df_reproduction = createDataFrame.calculateReproductionNumberForDataFrame(df)
    if selected_province:
        st.write(f"#### Evolvement of COVID-19 reproduction number for {selected_province}")
    elif selected_country:
        st.write(f"#### Evolvement of COVID-19 reproduction number for {selected_country}")
    elif selected_continent:
        st.write(f"#### Evolvement of COVID-19 reproduction number for {selected_continent}")
    else:
        st.write("### Global evolvement of COVID-19 reproduction number")

    df_population = createDataFrame.dataFrameToCasesPerMillion(df)
    fig3, ax3 = plt.subplots(figsize=((10,6)))
    ax3.plot(df_reproduction["Date"], df_reproduction["Reproduction Number"], label="Active Cases", color="blue")

    ax3.set_xlabel("Date")
    ax3.xaxis.set_major_locator(mdates.MonthLocator(interval=1))
    ax3.set_ylabel(r"$R_0$")
    ax3.legend()
    st.pyplot(fig3) # Plot selected country, continent or global for cases per million

# Top US Counties Tab
with tab4:
    st.header("Top 5 US Counties with Most Cases and Deaths")
    top_cases = df_usa_counties.groupby(["Admin2", "Province_State"], as_index=False)["Confirmed"].sum()
    top_cases = top_cases.nlargest(5, "Confirmed")

    top_deaths = df_usa_counties.groupby(["Admin2", "Province_State"], as_index=False)["Deaths"].sum()
    top_deaths = top_deaths.nlargest(5, "Deaths")

    st.write("### Top 5 Counties by Confirmed Cases")
    st.write(top_cases)

    st.write("### Top 5 Counties by Deaths")
    st.write(top_deaths)

# Case Fatality Rate Tab
with tab5:
    st.header("Case Fatality Rate Analysis")
    st.write("### Case Fatality Rate Over Time")

    # Calculate case fatality rate
    df_day["Case Fatality Rate"] = df_day["Deaths"] / df_day["Confirmed"]

    # Plot case fatality rate
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(pd.to_datetime(df_day["Date"]), df_day["Case Fatality Rate"], label="Case Fatality Rate")
    ax.set_xlabel("Date")
    ax.set_ylabel("Case Fatality Rate")
    ax.set_title("Case Fatality Rate Over Time")
    ax.legend()
    st.pyplot(fig)
