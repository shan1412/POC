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




class attendence(db.Model):
    roll_number = db.Column(db.Integer)
    student_name = db.Column(db.String(50), nullable=False)
    current_class= db.Column(db.Integer)
    date = db.Column(db.Date, nullable=False)
    attendance=db.Column(db.Integer)