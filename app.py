from flask import Flask, url_for, render_template, request, redirect, session
import secrets
import os
import re
from pymongo import MongoClient
from PIL import Image
from main import *
import time

from datetime import datetime
import pytz


app = Flask(__name__)
uri = "mongodb://localhost:27017"

# Create a new client and connect to the server
client = MongoClient(uri)
collection = client.WebDesign.MyBlog

# Get the current UTC time
utc_time = datetime.utcnow()

# Define the Indian Standard Time (IST) timezone
ist_timezone = pytz.timezone('Asia/Kolkata')


app.secret_key = b"e467b980fab392539c7ab1b0f85db21f14703bff1f8006c634b46ae24e2bdd5f"

app.config['UPLOAD_FOLDER'] = 'static/images'

# Fixed dimensions for thumbnails
THUMBNAIL_WIDTH = 400
THUMBNAIL_HEIGHT = 225

# Extract data from database


@app.route('/')
def homepage():
    allBlogs = get_dataset(short_content=True)
    return render_template('allBlogs.html', allBlogs=allBlogs)


@app.route('/<string:username>/<string:url>')
def blogpage(username, url):
    allBlogs = extract_dataset(username=username, short_content=False)
    if allBlogs == {}:
        return redirect('/404')

    profile_response = allBlogs['Profile']
    blog_response = allBlogs['Blogs']
    url_not_found = ''
    for blog in blog_response:
        if blog['url'] == url:
            allBlogs = blog | profile_response
            return render_template('blog.html', allBlogs=allBlogs)
        else:
            url_not_found = True

    if url_not_found == True:
        return redirect('/404')
        


@app.route('/<string:username>')
def profile(username):

    allBlogs = extract_dataset(username=username, short_content=True)
    if allBlogs == {}:
        return redirect('/404')
    return render_template('profile.html', allBlogs=allBlogs['Blogs'], profile_response=allBlogs['Profile'])


@app.route('/404')
def page_not_found():
    return render_template('404.html')


@app.route('/signin', methods=['GET', 'POST'])
def signin():
    if request.method == 'POST':
        email = request.form['emailInput']
        password = request.form['passwordInput']

        data = get_data(email)
        if data != '':
            queried_email = data['Profile']['email']
            queried_password = data['Profile']['password']
            if email == queried_email and password == queried_password:
                username = data['Profile']['username']

                return redirect(f'/{username}')
            else:
                return render_template('login.html', error='invalid credentials', email=email)

        return render_template('login.html', error='user not registered with us.')

    return render_template('login.html')


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form['nameInput']
        username = request.form['usernameInput']
        email = request.form['emailInput']
        password = request.form['passwordInput']
        # Convert the UTC time to IST
        ist_time = utc_time.replace(tzinfo=pytz.utc).astimezone(ist_timezone)

        # Format the IST time as month date, year hour:min:sec
        formatted_time = ist_time.strftime('%B %d, %Y %H:%M:%S')
        data = {
            username: {
                'Profile': {
                    'name': name,
                    'username': username,
                    'email': email,
                    'password': password,
                    'profile_picture': 'blank-profile-picture.jpg',
                    'profile_created': formatted_time,
                    'profile_summary': '',
                    'follower': 0,
                    'following': 0
                },
                'Blogs': [

                ]}
        }

        collection.insert_one(data)

        return redirect('/')
    return render_template('signup.html')


if __name__ == "__main__":
    app.run(debug=True, port=5500)
