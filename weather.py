import requests
import sys
import os
import json
from datetime import datetime

# ANSI color codes for terminal output
class Colors:
    BLUE = "\033[94m"
    CYAN = "\033[96m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    MAGENTA = "\033[95m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    RESET = "\033[0m"

# Weather condition icons (terminal friendly)
WEATHER_ICONS = {
    "clear sky": "☀️",
    "few clouds": "🌤️",
    "scattered clouds": "⛅",
    "broken clouds": "☁️",
    "overcast clouds": "☁️",
    "shower rain": "🌧️",
    "rain": "🌧️",
    "light rain": "🌦️",
    "moderate rain": "🌧️",
    "heavy intensity rain": "⛈️",
    "thunderstorm": "⛈️",
    "snow": "❄️",
    "light snow": "🌨️",
    "mist": "🌫️",
    "haze": "🌫️",
    "fog": "🌫️",
    "smoke": "🌫️",
}

API_KEY_FILE = os.path.join(os.path.expanduser("~"), ".weather_cli_key")


def get_api_key():
    """Load the API key from file or prompt the user to enter one."""
    if os.path.exists(API_KEY_FILE):
        with open(API_KEY_FILE, "r") as f:
            return f.read().strip()
    return None


def save_api_key(key):
    """Save the API key to a local file for future use."""
    with open(API_KEY_FILE, "w") as f:
        f.write(key)
    print(f"{Colors.GREEN}API key saved successfully.{Colors.RESET}")


def setup_api_key():
    """Walk the user through setting up their API key."""
    print(f"\n{Colors.BOLD}Weather CLI Setup{Colors.RESET}")
    print(f"{Colors.DIM}You need a free API key from OpenWeatherMap to use this tool.{Colors.RESET}")
    print(f"{Colors.DIM}Get one at: https://openweathermap.org/appid{Colors.RESET}\n")
    key = input(f"{Colors.CYAN}Enter your API key: {Colors.RESET}").strip()
    if key:
        save_api_key(key)
        return key
    else:
        print(f"{Colors.RED}No key entered. Exiting.{Colors.RESET}")
        sys.exit(1)


def get_icon(description):
    """Return a weather icon based on the description text."""
    desc = description.lower()
    for key, icon in WEATHER_ICONS.items():
        if key in desc:
            return icon
    return "🌍"


def fetch_weather(city, api_key):
    """Fetch current weather data from OpenWeatherMap API."""
    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {
        "q": city,
        "appid": api_key,
        "units": "metric"
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        if response.status_code == 401:
            print(f"{Colors.RED}Invalid API key. Run 'python weather.py --setup' to reconfigure.{Colors.RESET}")
            sys.exit(1)
        elif response.status_code == 404:
            print(f"{Colors.RED}City not found. Please check the spelling and try again.{Colors.RESET}")
            sys.exit(1)
        elif response.status_code != 200:
            print(f"{Colors.RED}API error (status {response.status_code}). Please try again later.{Colors.RESET}")
            sys.exit(1)

        return response.json()
    except requests.ConnectionError:
        print(f"{Colors.RED}No internet connection. Please check your network and try again.{Colors.RESET}")
        sys.exit(1)
    except requests.Timeout:
        print(f"{Colors.RED}Request timed out. Please try again.{Colors.RESET}")
        sys.exit(1)


def fetch_forecast(city, api_key):
    """Fetch 5 day forecast data from OpenWeatherMap API."""
    url = "https://api.openweathermap.org/data/2.5/forecast"
    params = {
        "q": city,
        "appid": api_key,
        "units": "metric",
        "cnt": 8  # Next 24 hours (3 hour intervals)
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        if response.status_code == 200:
            return response.json()
    except:
        pass
    return None


def display_weather(data):
    """Format and display the weather data in a beautiful terminal layout."""
    city = data["name"]
    country = data["sys"]["country"]
    temp = data["main"]["temp"]
    feels_like = data["main"]["feels_like"]
    humidity = data["main"]["humidity"]
    pressure = data["main"]["pressure"]
    wind_speed = data["wind"]["speed"]
    description = data["weather"][0]["description"]
    icon = get_icon(description)
    visibility = data.get("visibility", 0) / 1000  # Convert to km

    sunrise = datetime.fromtimestamp(data["sys"]["sunrise"]).strftime("%I:%M %p")
    sunset = datetime.fromtimestamp(data["sys"]["sunset"]).strftime("%I:%M %p")

    # Temperature color
    if temp >= 35:
        temp_color = Colors.RED
    elif temp >= 25:
        temp_color = Colors.YELLOW
    elif temp >= 15:
        temp_color = Colors.GREEN
    else:
        temp_color = Colors.CYAN

    print()
    print(f"  {Colors.BOLD}{Colors.BLUE}{'=' * 48}{Colors.RESET}")
    print(f"  {Colors.BOLD}  {icon}  Weather in {city}, {country}{Colors.RESET}")
    print(f"  {Colors.BLUE}{'=' * 48}{Colors.RESET}")
    print()
    print(f"  {Colors.BOLD}  {temp_color}{temp:.1f} C{Colors.RESET}  {Colors.DIM}(Feels like {feels_like:.1f} C){Colors.RESET}")
    print(f"  {Colors.DIM}  {description.capitalize()}{Colors.RESET}")
    print()
    print(f"  {Colors.CYAN}  Humidity     {Colors.RESET}{humidity}%")
    print(f"  {Colors.CYAN}  Wind Speed   {Colors.RESET}{wind_speed} m/s")
    print(f"  {Colors.CYAN}  Pressure     {Colors.RESET}{pressure} hPa")
    print(f"  {Colors.CYAN}  Visibility   {Colors.RESET}{visibility:.1f} km")
    print()
    print(f"  {Colors.YELLOW}  Sunrise      {Colors.RESET}{sunrise}")
    print(f"  {Colors.MAGENTA}  Sunset       {Colors.RESET}{sunset}")
    print()
    print(f"  {Colors.BLUE}{'=' * 48}{Colors.RESET}")
    print()


def display_forecast(data):
    """Display a compact 24 hour forecast."""
    if not data:
        return

    print(f"  {Colors.BOLD}  Upcoming Forecast{Colors.RESET}")
    print(f"  {Colors.DIM}  {'Time':<12} {'Temp':>6}  {'Description'}{Colors.RESET}")
    print(f"  {Colors.DIM}  {'-' * 40}{Colors.RESET}")

    for item in data["list"]:
        dt = datetime.fromtimestamp(item["dt"]).strftime("%I:%M %p")
        temp = item["main"]["temp"]
        desc = item["weather"][0]["description"]
        icon = get_icon(desc)

        if temp >= 30:
            tc = Colors.RED
        elif temp >= 20:
            tc = Colors.YELLOW
        else:
            tc = Colors.CYAN

        print(f"  {Colors.DIM}  {dt:<12}{Colors.RESET} {tc}{temp:>5.1f} C{Colors.RESET}  {icon} {desc}")

    print()


def print_help():
    """Display usage instructions."""
    print(f"""
{Colors.BOLD}Weather CLI{Colors.RESET}
{Colors.DIM}Get current weather and forecasts right in your terminal.{Colors.RESET}

{Colors.BOLD}Usage:{Colors.RESET}
    python weather.py <city>              Show current weather
    python weather.py <city> --forecast   Include 24h forecast
    python weather.py --setup             Configure your API key
    python weather.py --help              Show this help message

{Colors.BOLD}Examples:{Colors.RESET}
    python weather.py London
    python weather.py "Kuala Lumpur" --forecast
    python weather.py Tokyo
    """)


def main():
    args = sys.argv[1:]

    if not args or "--help" in args:
        print_help()
        return

    if "--setup" in args:
        setup_api_key()
        return

    api_key = get_api_key()
    if not api_key:
        api_key = setup_api_key()

    city = args[0]
    show_forecast = "--forecast" in args

    data = fetch_weather(city, api_key)
    display_weather(data)

    if show_forecast:
        forecast = fetch_forecast(city, api_key)
        display_forecast(forecast)


if __name__ == "__main__":
    main()
