# Max Diff Elo Rater
A barebones webapp I threw together to rank a long list of items using [Max Diff](https://en.wikipedia.org/wiki/MaxDiff). Rankings are determined by a simple [Elo system](https://en.wikipedia.org/wiki/Elo_rating_system) under the hood.

## Setup
This is a Python-based web application.

1. Install the Python dependencies in your virtual environment:
    
    `pip install -r requirements.txt`
2. Set the Flask environment variables:
    
    `export FLASK_APP=app`
    
    `export FLASK_ENV=development`
3. Input your list of items you want to rank in `items.csv`
4. Run the app using `flask run`. The app will be running at `localhost:5000`
