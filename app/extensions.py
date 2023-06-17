from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()   
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from credentials import *

engine = create_engine(f'postgresql+psycopg2://{username}:{password}@{host}:{port}/{database}')
Session = sessionmaker(bind=engine)

