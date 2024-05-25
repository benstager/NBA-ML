from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError

# Database connection parameters
db_username = 'postgres'
db_password = 'pacman561'
db_host = 'localhost'
db_port = '5432'  # Default PostgreSQL port is 5432
db_name = 'TESTING_RANKINGS'

# SQLAlchemy connection string
connection_string = f'postgresql://{db_username}:{db_password}@{db_host}:{db_port}/{db_name}'

try:
    # Create SQLAlchemy engine
    engine = create_engine(connection_string)
    
    # Test connection
    with engine.connect() as connection:
        print("Successfully connected to the database!")
except OperationalError as e:
    print(f"Failed to connect to the database: {e}")