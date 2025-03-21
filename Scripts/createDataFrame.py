import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.integrate import solve_ivp
import query_database
import sqlite3
import plotly.express as px

def createDataFrameOverTime(continent=None, country=None, province=None, startdate=None, enddate=None):
    connection = sqlite3.connect("Data/covid_database.db")

    complete_df = pd.read_csv("Data/complete.csv", parse_dates=["Date"])
    complete_df[["Confirmed", "Deaths", "Recovered", "Active"]] = complete_df[["Confirmed", "Deaths", "Recovered", "Active"]].fillna(0)


    cursor = connection.cursor()

    data_startdate, data_enddate = query_database.date_ranges(cursor)

    if not startdate:
        startdate = data_startdate
    
    if not enddate:
        enddate = data_enddate

    if startdate < data_startdate:
        startdate = data_startdate

    if enddate > data_enddate:
        enddate = data_enddate        

    if not continent:
        return  query_database.Total_Cases_Per_Day_Global(connection, startdate, enddate)
    
    if continent and not country:
        return query_database.Total_Cases_Per_Day_Continental(connection, continent, startdate, enddate)
    
    if continent and country and not province:
        return query_database.Total_Cases_Per_Day_Country(connection, continent, country, startdate, enddate)
    
    if continent and country and province:
        return query_database.Total_Cases_Per_Day_Province(connection, continent, country, province, startdate, enddate)
    
    return None

df = createDataFrameOverTime(continent="Western Pacific", country="China", province=None, startdate="2020-03-01")

def calculateReproductionNumberForDataFrame(df):
    # Estimator with the value given in the assignment
    gamma = 1 / 4.5

    # Calculate mu for each day in the dataframe
    df["mu"] = df["Total_Deaths"].diff() / df["Total_Active_Cases"]

    # Calculate beta for each day in the dataframe
    df["beta"] = (df["Total_Active_Cases"].diff() + df["mu"] * df["Total_Active_Cases"] + df["Total_Active_Cases"] * gamma) * df["Population"] / (df["Total_Active_Cases"] * (df["Population"] - df["Total_Confirmed_Cases"]))
    
    df["Reproduction Number"] = df["beta"] * gamma

    return df

def dataFrameToCasesPerMillion(df):
    million = 1000000 # for readability

    # Recalculates the numbers in terms of cases per million
    df["Total_Confirmed_Cases"] = df["Total_Confirmed_Cases"] * million / df["Population"]
    df["Total_Deaths"] = df["Total_Deaths"] * million / df["Population"]
    df["Total_Recovered"] = df["Total_Recovered"] * million / df["Population"]
    df["Total_Active_Cases"] = df["Total_Active_Cases"] * million / df["Population"]

    return df

print(dataFrameToCasesPerMillion(df))



        
        

