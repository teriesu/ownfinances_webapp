from .extensions import db 

from flask import Flask

app = Flask(__name__)

class Users(db.Model):

    __tablename__ = 'usuarios'
    
    user = db.Column(db.Text, primary_key=True)
    password = db.Column(db.Text, nullable=False)

    def __init__(self, user, password):
        self.user = user
        self.password = password

    def __repr__(self):
        return f'{self.user, self.password}'
    
    def to_dict(self):
        return {
            'user': self.user,
            'password': self.password
        }