from flask import render_template, url_for, flash, redirect, request
from website import app, db, bcrypt, text_detection, utilities, instance_start_time
from website.models import user_list, image_list
from website.forms import RegistrationForm, LoginForm, PictureForm
from flask_login import login_user, current_user, logout_user, login_required
from datetime import datetime
from werkzeug.utils import secure_filename
import os
import boto3
import time
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
import requests

#Initializations required, also getting current instance name to pass into metrics
cloudwatch = boto3.client('cloudwatch')
count = 0
UPLOAD_FOLDER = '/Users/ragnarok/Desktop/ece1779/a1/a1/user_images/'

#Get current instance ID
try:
    response = requests.get('http://169.254.169.254/latest/meta-data/instance-id')
    instance_id = response.text
except:
    instance_id = 'localhost'


# Defining a before_request to increment count each time we see a request
@app.before_request
def before_request():
    global count
    count += 1
    return


# APScheduler that pushes the HTTP request count to cloudwatch every minute, and resets count
def publish_metrics():
    global count
    global instance_id
    ## API to publish metrics
    response = cloudwatch.put_metric_data(
        Namespace='HTTP_Requests',
        MetricData=[
            {
                'MetricName': 'HTTP_Requests',
                'Dimensions':[
                    {
                    'Name': 'Instance_ID',
                    'Value': instance_id
                    },
                ],
                'Timestamp': datetime.utcnow(),
                'Unit': 'None',
                'Value': count
            },
        ]   
    )
    print('Pushing metrics now. Count and response: ', count, instance_id, response)
    count = 0
    
scheduler = BackgroundScheduler()
job = scheduler.add_job(publish_metrics, 'interval', minutes=1)
scheduler.start()

@app.route('/')
@app.route('/home')
def home():
    print(count)
    title = 'Home'
    user = 'Raghav'
    return render_template('home.html', title = title, user = user)

@app.route('/register', methods=['GET', 'POST'])
def register():
    print(count)
    if current_user.is_authenticated:
        flash('You are already logged in. Please log out to create a new account.', 'danger')
        return redirect(url_for('home'))
    form = RegistrationForm()
    title = 'Register'
    if form.validate_on_submit():
        #Generate a hashed-password, and store user + hashed pw in db
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = user_list(username=form.username.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Account created successfully. You can now log in with your username and password.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title=title, form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    print(count)
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    title = 'Log In'
    if form.validate_on_submit():
        #Query by email to see if it exists in db to login
        username = user_list.query.filter_by(username = form.username.data).first()
        if username and bcrypt.check_password_hash(username.password, form.password.data):
            login_user(username, remember=form.remember.data)

            #If a page accessible only to logged in users is accessed before logging in
            next_page = request.args.get('next')
            flash('Successfully logged in!', category='success')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Incorrect email or password', 'danger')
    return render_template('login.html', title=title, form=form)

@login_required
@app.route('/logout')
def logout():
    print(count)
    logout_user()
    return redirect(url_for('home'))

@login_required
@app.route('/images')
def images():
    print(count)
    title = 'Images'
    if not current_user.is_authenticated:
        flash('Please login to view your images', category='danger')
    thumbnail_path = os.path.join(app.root_path, 'static/thumbnails')
    images = [image for image in os.listdir(thumbnail_path) if current_user.username == image.split('_')[0]]
    
    #Temp files in mac
    if '.DS_Store' in images:
        images.remove('.DS_Store') 
    #Query into db to find all image names
    image_names = [image.__dict__['imagename'] for image in 
                image_list.query.filter_by(username=current_user.username).all()]
    return render_template('images.html', title=title, images=images)


#Uploads image file, stores image on filesystem, creates thumbnail, detects text, and stores modified image
@login_required
@app.route('/upload', methods=['GET', 'POST'])
def upload():
    print(count)
    if not current_user.is_authenticated:
        flash('Please login to access this route', category='danger')
        return redirect(url_for('login'))
    form = PictureForm()
    title = 'Upload'
    
    if form.validate_on_submit():
        if form.picture.data:
            s3 = boto3.client('s3')
            filename = secure_filename(form.picture.data.filename)
            hashed_filename = current_user.username + '_' + str(time.time()).replace('.', '_') + '_' + filename
            picture_path = os.path.join(app.root_path, 'static/user_images/' + hashed_filename)
            form.picture.data.save(picture_path)
            
            # Try to store in s3
            s3.upload_file(picture_path, 'my-test-bucket-ece1779', 'user_images/{}'.format(hashed_filename))

            image_details = image_list(imagename=hashed_filename, username=current_user.username)
            db.session.add(image_details)
            db.session.commit()

            #Create thumbnail
            thumbnail_path = os.path.join(app.root_path, 'static/thumbnails/')
            utilities.create_thumbnail(picture_path, thumbnail_path, s3=s3)

            #Finds text in the file, and stores it in '/static/output/'
            output_path = os.path.join(app.root_path, 'static/output/')
            text_detection.find_text(picture_path, output_path, s3=s3)

            # Remove file from temporary local storage
            if os.path.isfile(picture_path):
                #os.remove(picture_path)
                pass
        flash('Uploaded', category='success')
        return redirect(url_for('upload'))
    return render_template('upload.html', title=title, form=form)