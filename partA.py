import pandas as pd
import matplotlib.pyplot as plt  # ✅ Import this line
import datetime

# Load the dataset
df = pd.read_csv("project/Covid/day_wise.csv")

# Convert 'Date' column to datetime format
df["Date"] = pd.to_datetime(df["Date"])

# Create subplots
fig, axes = plt.subplots(nrows=3, ncols=1, figsize=(10, 12))  # Now plt is recognized

# Plot new cases
axes[0].plot(df["Date"], df["New cases"], color="blue", label="New Cases")
axes[0].set_title("New Cases Over Time")
axes[0].set_xlabel("Date")
axes[0].set_ylabel("New Cases")
axes[0].legend()

# Plot deaths
axes[1].plot(df["Date"], df["Deaths"], color="red", label="Deaths")
axes[1].set_title("Deaths Over Time")
axes[1].set_xlabel("Date")
axes[1].set_ylabel("Deaths")
axes[1].legend()

# Plot recovered cases
axes[2].plot(df["Date"], df["Recovered"], color="green", label="Recovered")
axes[2].set_title("Recovered Cases Over Time")
axes[2].set_xlabel("Date")
axes[2].set_ylabel("Recovered Cases")
axes[2].legend()

# Adjust layout
plt.tight_layout()
plt.show()