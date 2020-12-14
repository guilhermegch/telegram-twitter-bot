import tweepy
import logging

from settings.settings import API_KEY, API_SECRET_KEY, ACCESS_TOKEN, ACCESS_TOKEN_SECRET

# Set Tweepy
auth = tweepy.OAuthHandler(API_KEY, API_SECRET_KEY)
auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
api = tweepy.API(auth)

def check_user(username):
    '''Check if the user exists'''
    try:
        result = api.get_user(username)

        return True

    except tweepy.TweepError as error:
        if error.response.text.find('50'):
            logging.error(error.response.text)

            return False
        else: 
            raise Exception('Unknown error')

def get_user_data(username):
    '''Get the user first data'''
    result = api.get_user(username)

    name = result._json['name']
    bio = result._json['description']
    profile_image = result._json['profile_image_url_https'].replace('normal', '400x400')

    message = {'name': name, 'bio': bio, 'profile_image': profile_image}

    return message