import pandas as pd
import matplotlib.pyplot as plt
import numpy as np 
from scipy.optimize import minimize


df = pd.read_csv("Data\day_wise.csv")
df["Date"] = pd.to_datetime(df["Date"])

def plot_time_series(df, start_date, end_date):
    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)
    filtered_df = df[(df["Date"] >= start_date) & (df["Date"] <= end_date)]
    
    fig, axes = plt.subplots(nrows=3, ncols=1, figsize=(12, 10))
    axes[0].plot(filtered_df["Date"], filtered_df["New cases"], color="blue", label="New Cases")
    axes[0].set_title("New Cases Over Time")
    axes[0].set_xlabel("Date")
    axes[0].set_ylabel("New Cases")
    axes[0].legend()
    
    axes[1].plot(filtered_df["Date"], filtered_df["Deaths"], color="red", label="Deaths")
    axes[1].set_title("Deaths Over Time")
    axes[1].set_xlabel("Date")
    axes[1].set_ylabel("Deaths")
    axes[1].legend()
    
    axes[2].plot(filtered_df["Date"], filtered_df["Recovered"], color="green", label="Recovered")
    axes[2].set_title("Recovered Cases Over Time")
    axes[2].set_xlabel("Date")
    axes[2].set_ylabel("Recovered Cases")
    axes[2].legend()
    
    plt.tight_layout()
    plt.show()

plot_time_series(df, "2020-01-22", "2020-07-27")
plot_time_series(df, "2020-03-01", "2020-04-30")

# SIR Model
S0 = 17000000
I0 = df.loc[0, "Active"]
R0 = df.loc[0, "Recovered"]
D0 = df.loc[0, "Deaths"]
N = S0 + I0 + R0 + D0

alpha = 0.01
beta = 0.3
gamma = 0.1
mu = 0.01

S = [S0]
I = [I0]
R = [R0]
D = [D0]

for t in range(1, len(df)):
    delta_S = alpha * R[-1] - beta * S[-1] * I[-1] / N
    delta_I = beta * S[-1] * I[-1] / N - mu * I[-1] - gamma * I[-1]
    delta_R = gamma * I[-1] - alpha * R[-1]
    delta_D = mu * I[-1]
    
    S.append(S[-1] + delta_S)
    I.append(I[-1] + delta_I)
    R.append(R[-1] + delta_R)
    D.append(D[-1] + delta_D)

plt.figure(figsize=(10, 6))
plt.plot(df["Date"], S, label="Susceptible")
plt.plot(df["Date"], I, label="Infected")
plt.plot(df["Date"], R, label="Recovered")
plt.plot(df["Date"], D, label="Deceased")
plt.xlabel("Date")
plt.ylabel("Number of Individuals")
plt.title("SIR Model with Deaths")
plt.legend()
plt.tight_layout()
plt.show()


def error_function(params):
    beta, gamma = params
    I_pred = [I0]
    for t in range(1, len(df)):
        delta_I = beta * S[t-1] * I_pred[t-1] / N - gamma * I_pred[t-1]
        I_pred.append(I_pred[t-1] + delta_I)
    return np.sum((np.array(I_pred) - df["Active"])**2)

initial_guess = [0.3, 0.1]
result = minimize(error_function, initial_guess, bounds=[(0, 10), (0, 10)])
beta_est, gamma_est = result.x
R0_est = beta_est / gamma_est

print(f"Estimated beta: {beta_est}")
print(f"Estimated gamma: {gamma_est}")
print(f"Estimated R0: {R0_est}")

# Extra Inisht: Case Fatality Rate Over Time
df["Case Fatality Rate"] = df["Deaths"] / df["Confirmed"]

plt.figure(figsize=(10, 6))
plt.plot(df["Date"], df["Case Fatality Rate"], label="Case Fatality Rate")
plt.xlabel("Date")
plt.ylabel("Case Fatality Rate")
plt.title("Case Fatality Rate Over Time")
plt.legend()
plt.tight_layout()
plt.show()