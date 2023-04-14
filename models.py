from app import db,login_manager
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


