#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import pandas as pd
import json 
import time

# define Python user-defined exceptions
class Error(Exception):
  """Base class for other exceptions"""
  pass

class CaptchaRequired(Error):
  """Raised when the captcha is required"""
  pass

class DataNotAvailable(Error):
  """Raised when data are not available"""


# request to site
def req(url, INN, ts):
  headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
  params ={'vyp3CaptchaToken':'',
            'page':'',
            'query': INN,
            'region':'',
            'PreventChromeAutocomplete':''}
  res = ''
  # the delay time to prevent a captcha request
  time.sleep(ts)

  html_post = requests.post(url, data=params, headers=headers).text
  res_post = json.loads(html_post)

  token =  res_post['t']
  new_url = url + 'search-result/' + token
  html_get = requests.get(new_url, headers=headers).text 
  res_get = json.loads(html_get)['rows']

  return res_post, res_get

# cycle over all data
def cycle(url, data, ts):
  df = pd.DataFrame()
  INN_error = []
 
  for INN in data:
    INN = str(INN).strip()
    print(INN, end='\t')
    try:
      res_post, res_get = req(url, INN, ts)
      if res_post['captchaRequired']:
        raise CaptchaRequired
      if not res_get:
        raise DataNotAvailable
      df = df.append(res_get, ignore_index=True)
      print('Success')
    except CaptchaRequired:
      print('ERROR: captcha is required')
      INN_error.append(INN)
    except DataNotAvailable:
      print('ERROR: data are not available')        
      INN_error.append(INN)
    except:
      print('ERROR')
      INN_error.append(INN)
  if INN_error:
    print(len(INN_error), 'error INN:', INN_error)
  return df, INN_error


def file_save(df, filename):
  try:
    df.to_excel(filename)
    print(filename, 'saved successful')
  except:
    print(filename, 'save ERROR')


def main(data, ts=1):
  url = 'https://egrul.nalog.ru/'

  df, INN_error = cycle(url, data, ts)
  file_save(df, "output.xlsx")

  # repeat if errors
  if INN_error:
    print('Error repeat')
    df_error, INN_error_repeat = cycle(url, INN_error, ts)
    if not df_error.empty:
      file_save(df_error, "output_repeat.xlsx")


def test_data():
	"""
	test by the list of data
	"""
	data_pos = ['510480175992', '503410928602', '262406025003', '772605366657']
	data_neg = ['771506094152', '118774671888', '5044029634']
	
	main([*data_pos, *data_neg], ts=0)


def test_file():
	"""
	test by the external file 
	"""
	# get data from file of list
	INN_url = 'INN_test.txt'
	with open(INN_url) as f:
	  data = f.readlines()
	data = [s.strip() for s in data]
	main(data, ts=0)
  

if __name__ == "__main__":
	print("Test 1: reading from a list")
	test_data()
	print()
	
	print("Test 2: reading from a file")
	test_file()
  