import sqlite3
from Scripts.query_database import fetch_country_data
from Scripts.partThree import obtain_mu_hat, obtain_alpha_hat, obtain_beta_hat, produce_reproduction_number_trajectory

def test_database_connection():
    """Check if the database connection works and tables exist."""
    try:
        connection = sqlite3.connect("Data/covid_database.db")
        cursor = connection.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        connection.close()
        
        if tables:
            print("✅ Database connection successful. Tables found:", tables)
        else:
            print("❌ Database connection failed: No tables found.")
    except Exception as e:
        print("❌ Database connection failed:", e)

def test_fetch_country_data():
    """Test fetching COVID-19 data from the database."""
    country = "France"
    data = fetch_country_data(country)
    
    if data:
        print(f"✅ Data for {country} fetched successfully: {data}")
    else:
        print(f"❌ Failed to fetch data for {country}")

def test_parameter_functions():
    """Test the parameter estimation functions."""
    country = "France"
    mu_hat = obtain_mu_hat(country)
    alpha_hat = obtain_alpha_hat(country)
    beta_hat = obtain_beta_hat(country)

    print(f"Testing {country}...")
    print(f"✅ Estimated μ_hat (death rate): {mu_hat}")
    print(f"✅ Estimated α_hat (reinfection rate): {alpha_hat}")
    print(f"✅ Estimated β_hat (transmission rate): {beta_hat}")

def test_reproduction_number_trajectory():
    """Test the reproduction number trajectory function."""
    country = "France"
    days = 100
    print(f"🟢 Generating R₀ trajectory for {country} over {days} days...")
    produce_reproduction_number_trajectory(country, days)

if __name__ == "__main__":
    print("\n===== Running Tests =====\n")
    test_database_connection()
    test_fetch_country_data()
    test_parameter_functions()
    test_reproduction_number_trajectory()
    print("\n===== Tests Completed =====")
