Telegram Twitter Bot
====================
This is an implementation to join the Twitter and the Telegram APIs using **Python 3.9**

The bot sends to Telegram tweets in realtime from the users registered on the database.

## Setup ##

### Python environment ###
After cloning the repository, create a Python virtual environment, to don't mix with other libraries versions
```
python -m venv venv
```
Now activate the virtual environment:
```
source venv/bin/activate
```
And install the required packages:
```
pip install -r requirements.txt
```

### Twitter and Telegram keys ###
Go to the settings folder and fill a `.env` file with your Twitter Standard v1.1 and Telegram Bot keys following the `.env_example` file. On the first start of the bot, he will send your chat id on the message, to put on the `.env` file.

### SQLite ###
The database will be created by running the bot and adding the first username.

### Running ###
To start the bot:
```
python bot.py
```
To start receiving tweets, send `/startstream` to the bot.

## Limitations ##
This bot has the following limitations
- Even if you have access to an account with protected tweets (called status by the API), you can't receive them, since the API only returns public status as shown [here](https://developer.twitter.com/en/docs/twitter-api/v1/tweets/filter-realtime/overview)
    > Returns public statuses that match one or more filter predicates.
- The stream doesn't restart automatically if your stream suffers a disconnection. More about how to implement it [here](https://developer.twitter.com/en/docs/twitter-api/v1/tweets/filter-realtime/guides/connecting)
- After inserting a new user into the database, you'll need to manually stop the stream and start it again to receive this account tweets.

## Resources ##
This bot uses:
- [Twitter Standard v1.1 API](https://developer.twitter.com/en/docs/twitter-api/v1)
- [Telegram Bots](https://core.telegram.org/bots)
- [Tweepy](http://docs.tweepy.org/en/latest/)
- [Python Telegram Bot](https://python-telegram-bot.readthedocs.io/en/stable/)