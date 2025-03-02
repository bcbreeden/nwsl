# NWSL Insights
This project is dedicated to analyzing and collecting data related to the National Womens Soccer League. The data is displayed using Flask, a light weight library designed to create web applications.

## 📡 Data Source
**American Soccer Analysis API**
- [Documentation](https://app.americansocceranalysis.com/api/v1/__docs__/)

## 🧰 Setup
1. Clone repository
- `git clone https://github.com/bcbreeden/nwsl.git`
2. Create and active a Virtual Environment
- `python -m venv venv`
- `source venv/bin/activate` (MacOS/Linux)
- `venv\Scripts\activate` (Windows - Command Prompt)
- `.\venv\Scripts\Activate` (Windows - PowerShell)
3. Install Dependencies
- `pip install -r requirements.txt`
4. Initiate Data
- `python setup.py`
5. Start Flask
- `python flask_app.py`

## 🧪 Unit Tests
1. `coverage run -m unittest discover`
2. `coverage html`
3. /htmlcov/index.html