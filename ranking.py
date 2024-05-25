import pandas as pd
from sqlalchemy import create_engine
from nba_api.stats.endpoints import playercareerstats
from nba_api.stats.static import players
from nba_api.stats.static import teams 
from nba_api.live.nba.endpoints import scoreboard
from multiprocessing import Pool
from concurrent.futures import ProcessPoolExecutor
from joblib import Parallel, delayed
import pandas as pd
from nba_api.stats.endpoints import leaguegamefinder
import numpy as np

def find_games_by_year(all_games_df, date):
    games_year = all_games_df[all_games_df['GAME_DATE'] == date]
    return games_year

# Database connection details
db_username = 'postgres'
db_password = 'pacman561'
db_host = 'localhost'
db_port = '5433'
db_name = 'USER_RANKINGS'

# Create a SQLAlchemy engine
engine = create_engine(f'postgresql+psycopg2://{db_username}:{db_password}@{db_host}:{db_port}/{db_name}')

# necessary data
all_team_ids = [teams.teams[i][0] for i in range(len(teams.teams))]
all_team_names = [teams.teams[i][5] for i in range(len(teams.teams))]
team_id_dict = {i:j for i,j in zip(all_team_ids, all_team_names)}
dict_all_games = {team:leaguegamefinder.LeagueGameFinder(team_id_nullable=id).get_data_frames()[0] for team, id in zip(all_team_names,all_team_ids)}
all_games_df = pd.concat(list(dict_all_games.values()), axis=0)

print('------------------------------------')
print('         Starting database ....')
print('------------------------------------')
print()

first_name = input(('Enter your first name: '))
last_name = input(('Enter your last name: '))
rating_date = pd.Timestamp.now()

date = input('Please enter a date to view the games for that day (YYYY-MM-DD): ')
favorites = []
while date != 'Q' and date != 'q' and 'quit':
    games_date = find_games_by_year(all_games_df, date)
    print()

    while games_date.shape[0] == 0:
        date = input('No games were played that day. Try again (YYYY-MM-DD): ')
        games_date = find_games_by_year(all_games_df, date)

    records = [games_date.iloc[i] for i in range(games_date.shape[0])]
    records_dict = {i:j for i, j in zip(range(games_date.shape[0]), records)}
    for i in range(games_date.shape[0]):
        record = np.array(games_date.iloc[i][['TEAM_ABBREVIATION', 'GAME_DATE', 'MATCHUP', 'WL']])
        print(i + 1)
        print('Team:', record[0])
        print('Date:', record[1])
        print('Matchup:', record[2])
        print('Win or Loss?:', record[3])
        print()

    favorite_id = int(input('Enter the number of the game you want to rate: ')) - 1
    print('Please enter a rating for the game listed below! (scale 1 to 10, ex. 7):')
    print()
    record = np.array(games_date.iloc[favorite_id][['TEAM_ABBREVIATION', 'GAME_DATE', 'MATCHUP', 'WL']])
    print(favorite_id + 1)
    print('Team:', record[0])
    print('Date:', record[1])
    print('Matchup:', record[2])
    print('Win or Loss?:', record[3])
    print()
    rating = input('Rating: ')
    print()

    date = input('Please enter a date to view the games for that day (YYYY-MM-DD), when done type (quit, Q, or q): ')

    while games_date.shape[0] == 0:
        date = input('No games were played that day. Try again (YYYY-MM-DD): ')
        games_date = find_games_by_year(all_games_df, date)

    favorite = records_dict[favorite_id]
    favorites.append((rating,favorite))

print('---------------------------------------------------')
print("You selected: " + str(len(favorites)) + str(" games"))
print('---------------------------------------------------')
print("You selected the following games:")
print()
for i in favorites:
    print(str(i[1]['MATCHUP']) + str(' on ') + str(i[1]['GAME_DATE']))
    print('You rated it: ' + str(i[0]) + '/10')
    print()


matchups = [i[1]['MATCHUP'] for i in favorites]
game_date = [i[1]['GAME_DATE'] for i in favorites]
W_L = [i[1]['TEAM_ABBREVIATION'] for i in favorites]
WIN_LOSS = [i[1]['WL'] for i in favorites]
ratings = [i[0] for i in favorites]
first_names = np.tile(first_name, len(favorites))
last_names = np.tile(last_name, len(favorites))
timestamp = np.tile(rating_date, len(favorites))

ratings_session = pd.DataFrame({
    'Matchup': matchups,
    'Game date': game_date,
    'Team rated': W_L,
    'Win or loss?': WIN_LOSS,
    'Rating given':ratings,
    'User_First':first_names,
    'User_Last':last_names,
    'Date of rating': timestamp
})

ratings_session.to_sql('RATINGS_TEST', engine, index=False, if_exists='append')
print('Thanks for helping!')