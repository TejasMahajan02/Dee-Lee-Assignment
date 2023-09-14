from flask import Flask, url_for, render_template, request, redirect, session
import secrets
import os
import re
from pymongo import MongoClient
from PIL import Image
from main import *
import time

app = Flask(__name__)
uri = "mongodb://localhost:27017"

# Create a new client and connect to the server
client = MongoClient(uri)
collection = client.WebDesign.MyBlog

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
        formatted_time = get_current_time()
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


@app.route('/editor', methods=['GET', 'POST'])
def editor():
    if request.method == 'POST':
        title = request.form['titleField']
        desc = request.form['descField']
        image = request.files['imageField']
        category = request.form['selectField']
        formatted_time = get_current_time()
        blog_url = generate_blog_url(title)

        if image.filename:
            image_path = os.path.join(
                app.config['UPLOAD_FOLDER'], image.filename)

            image.save(image_path)

            # Open the image using Pillow
            img = Image.open(image_path)

            # Resize the image while maintaining aspect ratio
            img.thumbnail((THUMBNAIL_WIDTH, THUMBNAIL_HEIGHT))

            # Adjust quality as needed
            img.save(image_path, optimize=True, quality=50)

        data = {
            'title': title,
            'content': desc,
            'image': image.filename,
            'category': category,
            'url': blog_url,
            'likes': 0,
            'comments': [],
            'blog_published': formatted_time,
        }

        return data

    return render_template('editor.html')


@app.route('/update', methods=['GET', 'POST'])
def update():
    if request.method == 'POST':
        title = request.form['titleField']
        desc = request.form['descField']
        image = request.files['imageField']
        category = request.form['selectField']
        formatted_time = get_current_time()
        blog_url = generate_blog_url(title)

        if image.filename:
            image_path = os.path.join(
                app.config['UPLOAD_FOLDER'], image.filename)

            image.save(image_path)

            # Open the image using Pillow
            img = Image.open(image_path)

            # Resize the image while maintaining aspect ratio
            img.thumbnail((THUMBNAIL_WIDTH, THUMBNAIL_HEIGHT))

            # Adjust quality as needed
            img.save(image_path, optimize=True, quality=50)

        data = {
            'title': title,
            'content': desc,
            'image': image.filename,
            'category': category,
            'url': blog_url,
            'likes': 0,
            'comments': [],
            'blog_published': formatted_time
        }

        return data

    return render_template('update.html')


if __name__ == "__main__":
    app.run(debug=True, port=5500)
