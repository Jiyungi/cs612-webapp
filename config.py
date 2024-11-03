import os

class Config:
    SECRET_KEY = 'b7f3c9a8d1e4f5b6c7d8e9f0a1b2c3d4'  # Replace with a more secure method
    basedir = os.path.abspath(os.path.dirname(__file__))  # Root directory of the project
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'todo.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False