# COVID-19 Data Analysis and Visualization Dashboard

This project provides a comprehensive analysis and visualization of the COVID-19 pandemic using Python. It includes data wrangling, SQL queries, parameter estimation using the SIRD model, and an interactive dashboard built with Streamlit.

The objective is to derive meaningful insights from the pandemic data and present them in an accessible way to users such as analysts or policymakers.

## Project Structure

COVID/
│
├── Data/
│ ├── complete.csv
│ ├── covid_database.db
│ ├── day_wise.csv
│ 
├── Scripts/
│ ├── partOne.py
│ ├── query_database.py
│ ├── partThree.py
│ ├── partFour.py
│ ├── dashboard.py
│ 
├── README.md
├── requirements.txt # Vereiste Python-pakketten

## Table of contents
1. [How to Run the Dashboard](#how-to-run-the-dashboard)
2. [Dashboard Walkthrough](#dashboard-walkthrough)
3. [Technologies Used](#technologies-used)
4. [Data Sources](#data-sources)
5. [Notes](#notes)
6. [Contact](#contact)


## How to Run the Dashboard

1. Clone the repository or download the ZIP file and unzip it.
2. Install all required packages. 
    Run this in your terminal: pip install streamlit pandas matplotlib plotly numpy scipy
3. Navigate to the `Scripts` directory in your terminal.
4. Run the following command:
   ```bash
   streamlit run dashboard.py
5. The app will open in your default browser at http://localhost:8501.

## Dashboard Walkthrough

The dashboard consists of five interactive tabs and a sidebar for filtering by date, country, and continent.

### General Results

Summary Statistics: Presents aggregate statistics (mean, standard deviation, percentiles, etc.) for new cases, deaths, and recoveries.
Time Series Graphs:
New Cases Over Time: Visualizes how new cases evolve.
Deaths Over Time: Shows cumulative deaths.
Recovered Cases Over Time: Illustrates recovery trends.
Continent Comparison: A bar chart comparing total cases, deaths, and recoveries across continents.

### SIR Model

SIR Model with Deaths: Simulates COVID-19 dynamics using an extended SIRD model (Susceptible, Infected, Recovered, Deceased).
SIR Model vs Actual Data: Compares simulated infections to actual case numbers.
Parameter Estimation:
Estimated β (transmission rate)
Estimated γ (recovery rate)
Estimated R₀ (basic reproduction number)

### Data by Location

Filter by any country.
Displays up-to-date statistics like confirmed, deaths, recovered, active cases, and new daily counts.
Filter by continent (e.g., Europe, North America).
Shows all countries within the selected continent with relevant case data.

### Top US Counties

Top 5 Counties by Confirmed Cases: Highlights the five counties with the most total confirmed cases.
Top 5 Counties by Deaths: Displays the five counties with the highest death tolls.

### Case Fatality Rate

Plots the case fatality rate (deaths / confirmed cases) over time.
Helps monitor the lethality and trends of the virus.

## Technologies Used

- Python
- Streamlit
- SQLite3
- Pandas
- Matplotlib
- Plotly
- Scipy
- Git & Github

## Data Sources

- Johns Hopkins University COVID-19 Dataset
- Worldometer data scraped and processed for demographics and populations

## Notes

This project was created as part of the Data Engineering course for the Bachelor Business Analytics Vrije Universiteit Amsterdam.
All code and analyses are educational and exploratory in nature.

## Contact

Yasha Maas

Email: y.l.maas@student.vu.nl

Thomas van Leeuwen

Email: t.c.van.leeuwen@student.vu.nl

Pelle Hulshof

Email: p.m.c.hulshof@student.vu.nl

Tibor Praas

Email: t.j.praas@student.vu.nl


Project Link: https://github.com/tiborpraas/Covid
