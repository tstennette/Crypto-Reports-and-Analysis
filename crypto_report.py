import smtplib
import pandas as pd # DataFrame operations plus .csv I/O
import numpy as np # linear algebra
import os
from time import sleep
import coinmarketcapapi as coin
from datetime import datetime

sec_per_hr = 3600
end_time = "18:00"


def update_data(df):
	symbols = df['Symbol'].to_list()
	prices = []
	p_1hr = []
	p_7d = []
	p_24hr = []
	p_30d = []

	i = 0
	df['Date'] = datetime.now().strftime("%m-%d-%Y %H:%M")
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

	df['Price'] = prices
	df['1hr % Change'] = p_1hr
	df['24hr % Change'] = p_24hr
	df['7d % Change'] = p_7d
	df['30d % Change'] = p_30d
	df['Total Value'] = round((df['Price'] * df['Quantity']), 2)

	return df


def _ROI(df):
	asset_sum = round(df['Total Value'].sum() + int(df['Cash Left'][0]), 2)
	total_invested = float(df['Total Investment'][0])
	roi = round(((asset_sum - total_invested)/total_invested) * 100, 2)
	result = "ROI: {r}%  ({a}/{t})".format(r = roi, a = asset_sum, t = total_invested) 
	return result


def _buy_zone(df):
	buy_zone = df.loc[df['Price'] <= df['Buy Zone']]
	if(buy_zone.empty):
		return "*****Buy Zone Empty*****"

	df_final = buy_zone[['Symbol', 'Price']].set_index('Symbol')
	return df_final.sort_values(by = ['Price'])

def _sell_zone(df):
	sell_zone = df.loc[df['Price'] >= df['Sell Zone']]
	if(sell_zone.empty):
		return "*****Sell Zone Empty*****"
	df_final = sell_zone[['Symbol', 'Price']].set_index('Symbol')
	return df_final.sort_values(by = ['Price'])

def hr1_up(df):
	_up = df.loc[df['1hr % Change'] > 0]
	if (_up.empty):
		return "*****No hourly Gainers*****"
	final = _up[['Symbol', '1hr % Change']].set_index('Symbol')
	return final.sort_values(by = ['1hr % Change'], ascending=False)

def hr1_dwn(df):
	_dwn = df.loc[df['1hr % Change'] < 0]
	if (_dwn.empty):
		return "*****No hourly Downers*****"
	final = _dwn[['Symbol', '1hr % Change']].set_index('Symbol')
	return final.sort_values(by = ['1hr % Change'])

def _d7_up(df):
	d7_up = df.loc[df['7d % Change'] > 0]
	if (d7_up.empty):
		return "*****No weekly Gainers*****"
	final = d7_up[['Symbol', '7d % Change']].set_index('Symbol')
	return final.sort_values(by = ['7d % Change'], ascending=False)

def _d7_down(df):
	d7_dwn = df.loc[df['7d % Change'] < 0]
	if (d7_dwn.empty):
		return "*****No Weekly Downers*****"
	final = d7_dwn[['Symbol', '7d % Change']].set_index('Symbol')
	return final.sort_values(by = ['7d % Change'])

def _hr24_up(df):
	hr24_up = df.loc[df['24hr % Change'] > 0]
	if (hr24_up.empty):
		return "*****No daily Gainers*****"
	final = hr24_up[['Symbol', '24hr % Change']].set_index('Symbol')
	return final.sort_values(by = ['24hr % Change'], ascending=False)

def _hr24_down(df):
	hr24_dwn = df.loc[df['24hr % Change'] < 0]
	if (hr24_dwn.empty):
		return "*****No daily Downers*****"
	final = hr24_dwn[['Symbol', '24hr % Change']].set_index('Symbol')
	return final.sort_values(by = ['24hr % Change'])

def m_up(df):
	_up = df.loc[df['30d % Change'] > 0]
	if (_up.empty):
		return "*****No monthly Gainers*****"
	final = _up[['Symbol', '30d % Change']].set_index('Symbol')
	return final.sort_values(by = ['30d % Change'], ascending=False)

def m_dwn(df):
	_dwn = df.loc[df['30d % Change'] < 0]
	if (_dwn.empty):
		return "*****No monthly Downers*****"
	final = _dwn[['Symbol', '30d % Change']].set_index('Symbol')
	return final.sort_values(by = ['30d % Change'])

def get_message(df):
	message = """\
	Crypto Report {d}

	{r} 			

	Buy Zone

	{b}			

	Sell Zone

	{s}

	Hourly Gainers

	{h_up}

	Hourly Downers

	{h_dwn}

	Daily Gainers

	{hr24_up}

	Daily Downers

	{hr24_dwn}

	Weekly Gainers

	{d7_up}

	Weekly Downers

	{d7_dwn}

	Monthly Gainers

	{m_up}

	Monthly Downers

	{m_dwn}		

	""".format(d = df['Date'][0], r = _ROI(df), b = _buy_zone(df), s = _sell_zone(df),h_up = hr1_up(df), h_dwn = hr1_dwn(df), d7_up = _d7_up(df), d7_dwn = _d7_down(df), hr24_up = _hr24_up(df), hr24_dwn = _hr24_down(df), m_up = m_up(df), m_dwn = m_dwn(df))

	return message


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
	email = input("Enter Email address: ")
	password = input("Password: ")
	sleep_time = float(input("Enter time interval (hours) for report generation: "))

	while True:
		c_time = datetime.now().strftime("%H:%M")
		if c_time > end_time:
			print ("You are past the end time")
			break
		
		df1 = pd.read_csv('Crypto Assets.csv')
		df_final = update_data(df1)
		message = get_message(df_final)
		send_email(email, password, message)
		df_final.to_csv('Crypto Assets.csv', index= False)

		if sleep_time == 0:
			break
		else:
			sleep(sleep_time * sec_per_hr)

	print("Thank you for using Crypto Asset Reports! Have a great day :)")