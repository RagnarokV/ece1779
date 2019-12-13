from flask import Flask
import time

app = Flask(__name__)
app.config['SECRET_KEY'] = "c7e22c3ba94bd20390e19e9954796d8c"
instance_start_time = time.time()

from website import routes