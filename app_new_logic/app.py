from flask import Flask, render_template, request
from sqlalchemy import create_engine
from nba_api.stats.static import teams
from nba_api.stats.endpoints import leaguegamefinder
import pandas as pd
import datetime

database_type = 'postgresql'
dbapi = 'psycopg2'
endpoint = 'nba-ml-database.cdyyu2ws4399.us-east-2.rds.amazonaws.com'
user = 'postgres'
password = 'pacman561'
port = 5432
database = 'postgresNBA'

app = Flask(__name__)

# Define the database URL
DATABASE_URL = f"{database_type}+{dbapi}://{user}:{password}@{endpoint}:{port}/{database}"

# Create a SQLAlchemy engine
engine = create_engine(DATABASE_URL)

# Load data from the database
all_games_df = pd.read_sql("SELECT * FROM all_games_sorted", engine)

def find_games_by_year(all_games_df, date):
    games_year = all_games_df[all_games_df['GAME_DATE'] == date]
    return games_year

@app.route('/', methods=['GET', 'POST'])
def index():
    games = None
    date = None
    if request.method == 'POST':
        date = request.form['date']
        try:
            date = datetime.datetime.strptime(date, '%Y-%m-%d').date()
        except ValueError:
            return "Invalid date format. Please enter the date in YYYY-MM-DD format."

        games_date = find_games_by_year(all_games_df, str(date))
        if not games_date.empty:
            games = games_date.to_dict(orient='records')
        else:
            games = []

    return render_template('index.html', games=games, date=date)

@app.route('/rate', methods=['POST'])
def rate():
    ratings = []
    first_name = request.form['first_name']
    last_name = request.form['last_name']
    rating_date = pd.Timestamp.now()

    ratings_filled = False
    for game_id, rating in request.form.items():
        if game_id.startswith('rating_'):
            game_index = int(game_id.split('_')[1])
            game = request.form[f'game_{game_index}']
            if rating:  # Check if the rating is provided
                rating = int(rating)
                game_date, matchup, outcome = game.split('|')
                ratings.append({
                    'Matchup': matchup,
                    'Game date': game_date,
                    'Team rated': outcome,
                    'Win or loss?': outcome,
                    'Rating given': rating,
                    'User_First': first_name,
                    'User_Last': last_name,
                    'Date of rating': rating_date
                })
                ratings_filled = True

    if ratings_filled:
        ratings_df = pd.DataFrame(ratings)
        ratings_df.to_sql("user_rankings_new", engine, schema='public', index=False, if_exists='append')
        return "Thanks for helping! Your ratings have been recorded."
    else:
        return "Please provide at least one rating."

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
