import pandas as pd
from sqlalchemy import create_engine
import os
from dotenv import load_dotenv

print("Starting the data pump, sir... ⛽")
load_dotenv()


db_url = f"mysql+mysqlconnector://{os.getenv('MYSQL_USER')}:{os.getenv('MYSQL_PASSWORD')}@{os.getenv('MYSQL_HOST')}:{os.getenv('MYSQL_PORT')}/{os.getenv('MYSQL_DATABASE')}"
engine = create_engine(db_url)


df = pd.read_csv("data/road_accident_sample_500.csv")
df.to_sql('accident_records', con=engine, if_exists='replace', index=False)

print("Data successfully injected into MySQL! 🏁")
