from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
import time

# Directory where user images are uploaded
UPLOAD_FOLDER = '/Users/ragnarok/Desktop/ece1779/a1/a1/user_images/'

app = Flask(__name__)
app.config['SECRET_KEY'] = "c7e22c3ba94bd20390e19e9954796d8b"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'
instance_start_time = time.time()


from website import routes
