Route Optimization System

Description

This Route Optimization System is built using Python and Flask. It integrates real-time data from multiple APIs to calculate optimal routes, providing users with details like traffic conditions, weather, and estimated emissions. The system is equipped with a user-friendly interface designed with HTML and CSS.

Features

Optimized routes using real-time data
Traffic condition updates via TomTom API
Weather data using AQICN API
Emission calculations based on distance and fuel efficiency
User-friendly web interface
Installation

Requirements
Python 3.x
Flask
Requests
API keys for TomTom, AQICN, and Geocoding services

Setup

Clone the repository:
git clone <repository_url>
Navigate to the project folder:
cd <project_folder>
Install dependencies:
pip install -r requirements.txt
Add your API keys for TomTom, AQICN, and Geocoding in the API_KEYS section of the app.py file.
Run the Flask app:
python app.py
Visit http://127.0.0.1:5000/ in your browser to access the system.

Usage

Input start and end locations, vehicle type, and fuel efficiency.
View the calculated optimized route, traffic details, weather data, and emissions.
Contributing

Feel free to fork this repository, make changes, and submit pull requests.

License

This project is licensed under the MIT License.

