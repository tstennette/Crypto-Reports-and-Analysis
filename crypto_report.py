# The purpose of this program is to create a report on crypto assets 
# The report will contain data such as ROI and % gains/losses
import smtplib
import pandas as pd # DataFrame operations plus .csv I/O
import numpy as np # linear algebra
import os
from time import sleep
import coinmarketcapapi as coin
from datetime import datetime
import csv
import message as msg 
from getpass import getpass

sec_per_hr = 3600

'''
Gets the current data from CoinMarketCap API and updates dataframe
Parses a json object for each crypto to extract price and % changes
'''
def update_data(df):
	symbols = df['Symbol'].to_list()
	prices = [] # current price for each crypto
	p_1hr = [] # % change in 1 hr
	p_7d = [] # % change in 7 days
	p_24hr = [] # % change in 1 day
	p_30d = [] # % change in a month

	i = 0
	cmc = coin.CoinMarketCapAPI('935cfaa3-eb85-490c-9a9c-aba1bbc065b8')
	while i < len(symbols):
		json_data = cmc.cryptocurrency_quotes_latest(symbol=symbols[i])

		price = round(json_data.data[symbols[i]]['quote']['USD']['price'], 4)
		prices.append(price)

		p1hr = round(json_data.data[symbols[i]]['quote']['USD']['percent_change_1h'], 2)
		p_1hr.append(p1hr)

		p24hr = round(json_data.data[symbols[i]]['quote']['USD']['percent_change_24h'], 2)
		p_24hr.append(p24hr)

		p7d = round(json_data.data[symbols[i]]['quote']['USD']['percent_change_7d'], 2)
		p_7d.append(p7d)

		p30d = round(json_data.data[symbols[i]]['quote']['USD']['percent_change_30d'], 2)
		p_30d.append(p30d)	

		i = i + 1

	df['Date'] = datetime.now().strftime("%m-%d-%Y %H:%M")
	df['Price'] = prices
	df['1hr % Change'] = p_1hr
	df['24hr % Change'] = p_24hr
	df['7d % Change'] = p_7d
	df['30d % Change'] = p_30d
	df['Total Value'] = round((df['Price'] * df['Quantity']), 2)

	return df


def send_email(email, password, message):
	# creates SMTP session; 587 port # for gmail
	s = smtplib.SMTP('smtp.gmail.com', 587)
	# start Transport Layer Security
	s.starttls()
	s.login(email, password)
	s.sendmail(email, email, message)
	s.quit()


if __name__ == "__main__":

	print("Welcome to Crypto Asset Reports!\n")
	end_time = "20:05"
	#email = "ENTER EMAIL"
	#password = "ENTER PASSWORD"
	#sleep_time = 1 # number of hours in between reports; '0' to generate once
	email = input("Enter Email address: ")
	password = getpass()
	sleep_time = float(input("Enter time interval (hours) for report generation: "))

	while True:
		c_time = datetime.now().strftime("%H:%M")
		if c_time > end_time:
			print ("You are past the end time")
			break
		
		df1 = pd.read_csv('Crypto Assets.csv')
		df_final = update_data(df1)
		message = msg.get_message(df_final)
		send_email(email, password, message)
		df_final.to_csv('Crypto Assets.csv', index= False)

		if sleep_time == 0:
			break
		else:
			sleep(sleep_time * sec_per_hr)

	print("Thank you for using Crypto Asset Reports! Have a great day :)")
