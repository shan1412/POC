import os
import pandas as pd
import numpy as np
import openpyxl
import psycopg2
import datetime
from datetime import date
from flask import Flask, request, redirect, url_for,flash
from flask import render_template
from config import get_db_connection
from flask import make_response
from flask import abort
from flask import Flask
from flask import Flask
from flask_caching import Cache
from werkzeug.utils import secure_filename
from flask import send_from_directory
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import DataRequired
from flask_migrate import Migrate
from flask_login import LoginManager
from models import db,login_manager
from werkzeung.security import generate_password_hash,check_password_hash
from flask_login import UserMixin

@login_manager.user_loder
def load_user(user_id):
    return user.query.get(user_id)

class user(db.Model,UserMixin):
    
    __tablename_ = 'users'
    
    id = db.Column(db.Integer,primary_key =True)
    email =db.Column(db.String(64),unique=True,index=True)
    username=db.Column(db.String(64),unique=True,index=True)
    password_hash=db.Column(db.String(128))
    
    def __init__(self,email,username,password):
        self.email = email
        self.username = username
        self.password_hash = generate_password_hash(password)
        
    def check_password(self,password):
        return check_password_hash(self.password_hash,password)


