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

gamefinder = leaguegamefinder.LeagueGameFinder(team_id_nullable=1610612739)
games = gamefinder.get_data_frames()[0]

#  make an array of dataframes for all games
dict_all_games = {team:leaguegamefinder.LeagueGameFinder(team_id_nullable=id).get_data_frames()[0] for team, id in zip(all_team_names,all_team_ids)}
df = dict_all_games['Los Angeles Lakers'].head(5)

@app.route('/', methods=['GET', 'POST'])
def index():
    message = "Hello, World!"
    
    # Handle form submission
    if request.method == 'POST':
        user_input = request.form['user_input']
        return render_template('index.html', message=message, table=df.to_html(index=False), user_input=user_input)
    
    return render_template('index.html', message=message, table=df.to_html(index=False))

if __name__ == '__main__':
    app.run(debug=True)