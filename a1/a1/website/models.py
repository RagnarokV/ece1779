from website import db, login_manager
from flask_login import UserMixin

@login_manager.user_loader
def load_user(username):
    return user_list.query.get(username)

class user_list(db.Model, UserMixin):
    username = db.Column(db.String(20), unique=True, nullable=False, primary_key=True)
    password = db.Column(db.String(80), nullable=False)
    def __repr__(self):
        return f"User('{self.username}')"
    
    def get_id(self):
           return (self.username)

class image_list(db.Model):
    imagename = db.Column(db.String(100), unique=True, nullable=False, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
