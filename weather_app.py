import requests
from datetime import datetime
import tkinter as tk
from tkinter import messagebox
from tkinter import PhotoImage
from geopy.geocoders import Nominatim
import socket
import matplotlib.pyplot as plt

# Function to fetch current weather data
def get_weather():
    city = city_entry.get()
    if not city:
        # Try to detect the user's location
        city = get_location()
        if not city:
            messagebox.showwarning("Input Error", "Please enter a city name.")
            return

    api_key = "9f1c296c47e6477fa8f61d1511cd17c1"  # Replace with your API key
    unit = unit_var.get()  # Get the selected unit
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units={unit}"

    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an error for bad status codes
        data = response.json()

        # Extract weather information
        weather = data["weather"][0]["description"]
        temperature = data["main"]["temp"]
        humidity = data["main"]["humidity"]
        wind_speed = data["wind"]["speed"]
        pressure = data["main"]["pressure"]
        sunrise = datetime.fromtimestamp(data["sys"]["sunrise"]).strftime("%H:%M:%S")
        sunset = datetime.fromtimestamp(data["sys"]["sunset"]).strftime("%H:%M:%S")

        # Create the result string
        result = (
            f"Weather in {city}:\n"
            f"Condition: {weather}\n"
            f"Temperature: {temperature}°{'C' if unit == 'metric' else 'F'}\n"
            f"Humidity: {humidity}%\n"
            f"Wind Speed: {wind_speed} m/s\n"
            f"Pressure: {pressure} hPa\n"
            f"Sunrise: {sunrise}\n"
            f"Sunset: {sunset}"
        )

        # Display weather information
        messagebox.showinfo("Weather Information", result)

        # Save weather data to a file
        with open("weather_data.txt", "a") as file:
            file.write(result + "\n\n")
        print("Weather data saved to 'weather_data.txt'.")

        # Display weather icon
        display_icon(weather)

    except requests.exceptions.RequestException as e:
        messagebox.showerror("Error", f"Failed to fetch weather data. Error: {e}")
    except KeyError:
        messagebox.showerror("Error", "Invalid city name or API key. Please check your input.")

# Function to fetch and display 5-day forecast
def get_forecast():
    city = city_entry.get()
    if not city:
        messagebox.showwarning("Input Error", "Please enter a city name.")
        return

    api_key = "9f1c296c47e6477fa8f61d1511cd17c1"  # Replace with your API key
    unit = unit_var.get()  # Get the selected unit
    url = f"http://api.openweathermap.org/data/2.5/forecast?q={city}&appid={api_key}&units={unit}"

    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an error for bad status codes
        data = response.json()

        # Debug: Print the API response
        print("API Response:", data)

        # Check if the response contains forecast data
        if "list" not in data:
            messagebox.showerror("Error", "No forecast data found. Please check the city name.")
            return

        # Extract forecast information
        forecast = ""
        for item in data["list"][:8]:  # Show only the first 8 entries (24 hours)
            date = datetime.fromtimestamp(item["dt"]).strftime("%Y-%m-%d %H:%M:%S")
            weather = item["weather"][0]["description"]
            temperature = item["main"]["temp"]
            humidity = item["main"]["humidity"]

            forecast += (
                f"Date: {date}\n"
                f"Condition: {weather}\n"
                f"Temperature: {temperature}°{'C' if unit == 'metric' else 'F'}\n"
                f"Humidity: {humidity}%\n"
                "-----------------------------\n"
            )

        # Display forecast information
        messagebox.showinfo("24-Hour Forecast", forecast)

        # Plot temperature trends
        plot_temperature(data)

    except requests.exceptions.RequestException as e:
        messagebox.showerror("Error", f"Failed to fetch forecast data. Error: {e}")
    except KeyError as e:
        messagebox.showerror("Error", f"Invalid data format. KeyError: {e}")

# Function to clear the city entry field
def clear_entry():
    city_entry.delete(0, tk.END)

# Function to display weather icon
def display_icon(weather_condition):
    if "clear" in weather_condition.lower():
        icon_label.config(image=sun_icon)
    elif "cloud" in weather_condition.lower():
        icon_label.config(image=cloud_icon)
    elif "rain" in weather_condition.lower():
        icon_label.config(image=rain_icon)
    else:
        icon_label.config(image=None)

# Function to get the user's location
def get_location():
    try:
        # Get the user's IP address
        hostname = socket.gethostname()
        ip_address = socket.gethostbyname(hostname)

        # Use geopy to get the location
        geolocator = Nominatim(user_agent="weather_app")
        location = geolocator.geocode(ip_address)

        if location:
            return location.address
        else:
            return None
    except Exception as e:
        print(f"Error detecting location: {e}")
        return None

# Function to plot temperature trends
def plot_temperature(data):
    dates = []
    temperatures = []

    for item in data["list"][:8]:  # Use the first 8 entries (24 hours)
        date = datetime.fromtimestamp(item["dt"]).strftime("%H:%M")
        temperature = item["main"]["temp"]

        dates.append(date)
        temperatures.append(temperature)

    # Plot the data
    plt.figure(figsize=(8, 4))
    plt.plot(dates, temperatures, marker="o")
    plt.title("24-Hour Temperature Trend")
    plt.xlabel("Time")
    plt.ylabel(f"Temperature (°{'C' if unit_var.get() == 'metric' else 'F'})")
    plt.grid(True)
    plt.show()

# Create the main window
root = tk.Tk()
root.title("Weather App")

# Load weather icons (replace with your icon file paths)
sun_icon = PhotoImage(file="sun.png")  # Replace with the path to your sun icon
cloud_icon = PhotoImage(file="cloud.png")  # Replace with the path to your cloud icon
rain_icon = PhotoImage(file="rain.png")  # Replace with the path to your rain icon

# Create and place widgets
city_label = tk.Label(root, text="Enter City:")
city_label.pack(pady=5)

city_entry = tk.Entry(root, width=30)
city_entry.pack(pady=5)

unit_var = tk.StringVar(value="metric")  # Default to Celsius
unit_options = ["metric", "imperial"]
unit_menu = tk.OptionMenu(root, unit_var, *unit_options)
unit_menu.pack(pady=5)

get_weather_button = tk.Button(root, text="Get Weather", command=get_weather)
get_weather_button.pack(pady=5)

forecast_button = tk.Button(root, text="24-Hour Forecast", command=get_forecast)
forecast_button.pack(pady=5)

clear_button = tk.Button(root, text="Clear", command=clear_entry)
clear_button.pack(pady=5)

icon_label = tk.Label(root)
icon_label.pack(pady=5)

# Run the application
root.mainloop()



    #"9f1c296c47e6477fa8f61d1511cd17c1"