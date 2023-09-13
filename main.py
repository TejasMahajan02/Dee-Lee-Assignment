from pymongo import MongoClient
from datetime import datetime
import pytz
import re

uri = "mongodb://localhost:27017"

# Create a new client and connect to the server
client = MongoClient(uri)
collection = client.WebDesign.MyBlog


def get_dataset(short_content=True):

    object_ids = [i['_id'] for i in collection.find()]

    # it work when no argumenst passed
    allBlogs = []

    for obj_id in object_ids:
        query = {'_id': obj_id}
        query_response = collection.find_one(query)
        username_res = list(query_response.keys())[-1]
        # get profile data
        profile_response = query_response[username_res]['Profile']
        # deleting email and password field
        del profile_response['email']
        del profile_response['password']

        # get blog content
        blog_response = query_response[username_res]['Blogs']
        for blog in blog_response:
            if short_content == True:
                blog['content'] = blog['content'][:100]
            single_document = profile_response | blog
            allBlogs.append(single_document)

    # it will return all blog documents with profile and each single blogs merged
    return allBlogs


def extract_dataset(email=None, username=None, short_content=True):

    object_ids = [i['_id'] for i in collection.find()]

    for obj_id in object_ids:
        query = {'_id': obj_id}
        query_response = collection.find_one(query)
        username_res = list(query_response.keys())[-1]
        # if username argument is passed
        if username is not None:
            # Check if username is correct and exist in database
            if username_res == username:
                dataset = query_response[username_res]
                # deleting email and password field
                del dataset['Profile']['email']
                del dataset['Profile']['password']

                if short_content == True:
                    for blog in dataset['Blogs']:
                        blog['content'] = blog['content'][:100]

                # it will return only one document with profile and blogs as main keys
                return dataset

        # if email argument is passed
        if email is not None:
            # Check if email is correct and exist in database
            email_res = query_response[username_res]['Profile']['email']
            if email_res == email:
                # get profile content
                dataset = query_response[username_res]
                if short_content == True:
                    for blog in dataset['Blogs']:
                        blog['content'] = blog['content'][:100]
                # it will return only one document with profile and blogs as main keys
                return dataset

    return {}


def get_current_time():
    # Get the current UTC time
    utc_time = datetime.utcnow()

    # Define the Indian Standard Time (IST) timezone
    ist_timezone = pytz.timezone('Asia/Kolkata')
    # Convert the UTC time to IST
    ist_time = utc_time.replace(tzinfo=pytz.utc).astimezone(ist_timezone)

    # Format the IST time as month date, year hour:min:sec
    formatted_time = ist_time.strftime('%B %d, %Y %H:%M:%S')
    return formatted_time


def generate_blog_url(input_string):
    blog_url = '-'.join([word for word in input_string.strip().split()
                        if word.isalnum()])
    return blog_url
