import tweepy
import sys

from settings.settings import (
    API_KEY,
    API_SECRET_KEY,
    ACCESS_TOKEN,
    ACCESS_TOKEN_SECRET,
)
from src.database import list_users_database
from settings.settings import TELEGRAM_TOKEN
from telegram.ext import Updater

chat_id = sys.argv[1]

updater = Updater(TELEGRAM_TOKEN)

# Set Tweepy
auth = tweepy.OAuthHandler(API_KEY, API_SECRET_KEY)
auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
api = tweepy.API(auth)


# Create an array of user ids
user_list = []
ids_list = []

for user in list_users_database():
    user_list.append(user)
    ids_list.append(api.get_user(user)._json['id_str'])

ids = ','.join(ids_list)


# Create the class to receive the streams
class MyStreamListener(tweepy.StreamListener):
    def on_status(self, status):
        # Get status data
        username = status.user.screen_name.lower()
        text = status.text
        status_id = status.id

        link = f'https://twitter.com/{username}/status/{status_id}'

        mensagem = f'{username} tweeted:\n{text}\n\n{link}\n'

        if username not in user_list:
            return

        # Send the status to Telegram 
        updater.bot.sendMessage(chat_id = chat_id, text = mensagem)

        # Check if the tweet have media
        try:
            for media in status.extended_entities['media']:
                if media['type'] == 'photo':
                    base_url = media['media_url_https'].split('.')[0:-1]
                    base_url = '.'.join(base_url)
                    url = base_url + '?format=jpg&name=large'
                    updater.bot.sendPhoto(chat_id = chat_id, photo = url)
                    updater.bot.sendMessage(chat_id = chat_id, text = url)

                if media['type'] == ('video' or 'animated_gif'):
                    bitrate_list = []
                    # Gets the video with max bitrate
                    for bitrate in media['video_info']['variants']:
                        try:
                            bitrate_list.append(bitrate['bitrate'])
                        except KeyError:
                            bitrate_list.append(0)
                            pass
                    max_index = bitrate_list.index(max(bitrate_list))
                    url = media['video_info']['variants'][max_index]['url']
                    updater.bot.sendVideo(chat_id = chat_id, video = url)
                    updater.bot.sendMessage(chat_id = chat_id, text = url)

        except AttributeError:
            return

    def on_error(self, status_code):
        if status_code == 420:
            return False


myStreamListener = MyStreamListener()
mystream = tweepy.Stream(auth = api.auth, listener = myStreamListener)

updater.bot.sendMessage(chat_id = chat_id, text = 'Stream started!')

mystream.filter(follow = [ids])