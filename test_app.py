from flask import Flask, render_template, request
import pandas as pd
from nba_api.stats.endpoints import playercareerstats
from nba_api.stats.static import players
from nba_api.stats.static import teams 
from nba_api.live.nba.endpoints import scoreboard
from multiprocessing import Pool
from concurrent.futures import ProcessPoolExecutor
from joblib import Parallel, delayed
import pandas as pd
from nba_api.stats.endpoints import leaguegamefinder

# def app
app = Flask(__name__)


all_team_ids = [teams.teams[i][0] for i in range(len(teams.teams))]
all_team_names = [teams.teams[i][5] for i in range(len(teams.teams))]
team_id_dict = {i:j for i,j in zip(all_team_ids, all_team_names)}
dict_all_games = {team:leaguegamefinder.LeagueGameFinder(team_id_nullable=id).get_data_frames()[0] for team, id in zip(all_team_names,all_team_ids)}
all_games_df = pd.concat(list(dict_all_games.values()), axis=0)
df = dict_all_games['Los Angeles Lakers'].head(5)


gamefinder = leaguegamefinder.LeagueGameFinder(team_id_nullable=1610612739)
games = gamefinder.get_data_frames()[0]

def find_games_by_year_api_test(year):
    games_year = all_games_df[all_games_df['GAME_DATE'].str.contains(str(year))]
    return games_year.head(5)

def find_games_by_year(year):
    games_year = all_games_df[all_games_df['GAME_DATE'].str.contains(str(year))]
    return games_year

def find_games_by_team(team_str):
    games_team = all_games_df[all_games_df['TEAM_NAME'].str.contains(team_str)]
    return games_team

def find_games_by_matchup(team_1, team_2):
    team_1 = team_1.lower()
    team_2 = team_2.lower()
    games_matchup = all_games_df[(all_games_df['MATCHUP'].str.contains(team_1.upper())) & (all_games_df['MATCHUP'].str.contains(team_2.upper()))]

    return games_matchup

"""
def process_form():
    # Get user input from the form
    input_data = request.form.get('input_data')

    # Call the function with user input
    df = find_games_by_year_api_test(input_data)

    # Process the DataFrame as needed (e.g., convert to HTML)
    html_table = df.to_html()

    # Return the processed data to the frontend
    return render_template('result.html', html_table=html_table)
"""

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Get the input year from the form
        input_year = request.form.get('input_data')

        # Call the function to find games by year
        df = find_games_by_year_api_test(input_year)

        # Process the DataFrame to HTML
        html_table = df.to_html()

        # Render the result template with the HTML table
        return render_template('result.html', html_table=html_table)
    else:
        # Render the index template for the initial page load
        return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)