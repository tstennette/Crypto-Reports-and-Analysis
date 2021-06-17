import os
import tweepy as tw
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

consumer_key= 'ENTER API KEY'
consumer_secret= 'ENTER SECRET KEY'
access_token= 'ENTER ACCESS TOKEN'
access_token_secret= 'ENTER SECRET TOKEN'

auth = tw.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tw.API(auth, wait_on_rate_limit=True)

d = pd.read_csv("/Users/MacBookPro/Dropbox/Side data projects/Crypto-Reports-and-Analysis/Crypto Assets.csv")
sym = d["Symbol"].tolist()
names = d["Name"].tolist()
others = ['cryptocurrency', 'crypto', 'defi', 
            'smart contracts', 'NFT', 'Altcoins', 'bullish', 'bearish', 
            'blockchain', 'bear market', 'bull market', 'alts']
filter_list = sym + names + others
max_tweets = 200

def update_followers(ap):
    
    # gets full list of accounts I follow
    friend_list = []
    for friend in tw.Cursor(ap.friends).items():
        friend_list.append(friend.screen_name)
    
    df = pd.DataFrame(friend_list,columns=['Followed Accounts'])
    return df


def get_followers_tweets(d, count):
    my_followers = d.values.tolist()
    dates = []
    accs = []
    tweets_ = []
    i = 0
    while i < len(my_followers):
        f = str(''.join(my_followers[i]))
        tweets = api.user_timeline(screen_name= f, 
                           # 200 is the maximum allowed count
                           count=count,
                           include_rts = False,
                           # Necessary to keep full_text 
                           # otherwise only the first 140 words are extracted
                           tweet_mode = 'extended'
                           )
        for info in tweets:
             if any(x in info.full_text for x in filter_list):                  
                 dates.append(info.created_at)
                 accs.append(f)
                 tweets_.append(info.full_text)
        i = i + 1
                
    df_final = pd.DataFrame(columns = ['Date/Time', 'Account','Tweet'])
    df_final['Date/Time'] = dates
    df_final['Account'] = accs
    df_final['Tweet'] = tweets_
    return df_final


def process_old_data():
	df = pd.read_csv('crypto_tweets.csv')
	df['Date/Time'] = pd.to_datetime(df['Date/Time'])
	return df


if __name__ == "__main__":
	print("Welcome to Your Followers Crypto Tweets!")
	df_old = process_old_data()
	prev_time = max(df_old['Date/Time'])

	f = update_followers(api)
	df_new = get_followers_tweets(f, max_tweets)
	df_new = df_new[df_new['Date/Time'] > prev_time]
	df_final = df_old.append(df_new)
	df_final.sort_values(by='Date/Time', ascending = False, inplace=True)
	df_final.to_csv('crypto_tweets.csv', index = False)
