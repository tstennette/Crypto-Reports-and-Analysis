import os
import tweepy as tw
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

#consumer_key= 'ENTER API KEY'
#consumer_secret= 'ENTER SECRET KEY'
#access_token= 'ENTER ACCESS TOKEN'
#access_token_secret= 'ENTER SECRET TOKEN'

consumer_key= 'ZfiVcvMgHDRq5qv6Kx4jZ7pDV'
consumer_secret= 'Wgn6nhTZqY5eZ8o3YLbbg2eyzw4u9eiUxHTnKPhx6jW9Fv3Twf'
access_token= '1311507395311366144-AmEWKKujJUZMs8V0ME65vt5MSCjsp4'
access_token_secret= 'lS6g8DJTlBSdUEb8ynRwhsb24ueVk4YIJwrXkmmvPiAyx'

auth = tw.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tw.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)

d = pd.read_csv("/Users/MacBookPro/Dropbox/Side data projects/Crypto-Reports-and-Analysis/Crypto Assets.csv")
sym = d["Symbol"].tolist()
names = d["Name"].tolist()
others = ['cryptocurrency', 'crypto', 'decentralized', 
			'smart contracts', 'NFT', 'Altcoins', 
			'blockchain', 'alts', 'stablecoin',
		   'digital asset', 'USDC', 'DOGE']
filter_list = sym + names + others
filter_list.remove('ONE')
filter_list.remove('Maker')
filter_list.remove('UNI')
max_tweets = 50
begin_invest_date = "04-17-2021 13:00:00"

def update_followers():
	
	# gets full list of accounts I follow
	friend_list = []
	for friend in tw.Cursor(api.friends).items():
		friend_list.append(friend.screen_name)
	
	df = pd.DataFrame(friend_list,columns=['Followed Accounts'])
	return df


def get_followers_tweets(d):
	my_followers = d.values.tolist()
	#my_followers = ['EthereumFear']
	dates = []
	accs = []
	tweets_ = []
	i = 0
	while i < len(my_followers):
		fo = str(''.join(my_followers[i]))
		print(fo)
		tweets = api.user_timeline(screen_name= fo, 
						   # 200 is the maximum allowed count
						   count=max_tweets,
						   include_rts = False,
						   # Necessary to keep full_text 
						   # otherwise only the first 140 words are extracted
						   tweet_mode = 'extended'
						   )
		for info in tweets:
			 if any(x in info.full_text for x in filter_list):                  
				 dates.append(info.created_at)
				 accs.append(fo)
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
	f = update_followers()
	df_new = get_followers_tweets(f)
	df_new = df_new[df_new['Date/Time'] > prev_time]
	df_final = df_old.append(df_new)
	df_final = df_final[df_final['Date/Time'] >= begin_invest_date]
	df_final.sort_values(by='Date/Time', ascending = False, inplace=True)
	df_final.to_csv('crypto_tweets.csv', index = False)
