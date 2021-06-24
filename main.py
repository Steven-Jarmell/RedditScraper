from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from collections import Counter
import requests
import csv
import os.path
import numpy as np
from datetime import date, timedelta
from dateutil.parser import parse
import pandas as pd


DAILY_URL = "https://www.reddit.com/r/wallstreetbets/search/?q=flair%3A%22Daily%20Discussion%22&restrict_sr=1&sort=new"
WEEKEND_URL = "https://www.reddit.com/r/wallstreetbets/search/?q=flair%3A%22Weekend%20Discussion%22&restrict_sr=1&sort="
FILE_NAME = "symbols.txt"


def create_driver(URL):
    PATH = "C:\Program Files (x86)\chromedriver.exe" #Sets up the path for the driver
    chrome_options = Options() #Adds options in order to disable the notification that would pop up
    chrome_options.add_argument("--disable-notifications")
    driver = webdriver.Chrome(options=chrome_options, executable_path = PATH) #Creates the driver
    driver.get(URL) #Gets either the daily url or weekend url
    return driver

def get_comment_thread_link(driver, day_to_analyze):
    thread_links = driver.find_elements_by_xpath('//*[@class= "_eYtD2XCVieq6emjKBH3m"]') #Find the element which is the discussion header | Class is the same whether it is daily or weekend
    for link in thread_links:
        if link.text.startswith('Daily Discussion Thread'): #If the thread is daily discussion it gets the link for the post
            date = "".join(link.text.split(' ')[-3:])
            parsed = parse(date)
            if parse(str(day_to_analyze)) == parsed:
                thread_link = link.find_element_by_xpath('../..').get_attribute('href')
                            
        if link.text.startswith('Weekend'): #If the thread is a weekend discussion it gets the link
            date = "".join(link.text.split(' ')[-3:])             
            parsed = parse(date)
            if parse(str(day_to_analyze)) == parsed:
                thread_link = link.find_element_by_xpath('../..').get_attribute('href')
            
        
    thread_id = thread_link.split('/')[6] # *****This returns a single id, which is the last thread to be processed. Should change to a list containing all the IDs
    driver.close() #Closes the driver, as it is now unneeded
    return thread_id    


def get_comment_ids(thread_id):
    html = requests.get(f'https://api.pushshift.io/reddit/submission/comment_ids/{thread_id}') #Uses the pushshift API to get individual comment IDs
    comment_id_list = html.json() # Gets a json version of the comment ID

    return comment_id_list

def create_symbol_list():
    with open("symbols", "r") as file: #Opens the symbols file
        stock_symbols = file.readlines() #Reads the file
        symbol_list = [] #Creates a list which will contain the symbols
        for symbol in stock_symbols:
            symbol = symbol.replace('\n', '') #Gets rid of the separation inside the text file, and uts the symbols side by side separated by a comma
            symbol_list.append(symbol) #Puts the symbols in the list
    return symbol_list

def get_comments(comment_list):
    return requests.get(f'https://api.pushshift.io/reddit/comment/search?ids={comment_list}&fields=body&size=1000').json()
    

def get_stock_list(actual_comments, stocks_list):
    stock_dict = Counter()
    for comment in actual_comments['data']:
        for stock in stocks_list:
            if stock in comment['body']:
                stock_dict[stock] += 1
    return stock_dict

def get_stock_count(stock_dict, comments_list, stocks_list):
    orig_list = np.array(comments_list['data'])
    remove_me = slice(0,1000)
    cleaned = np.delete(orig_list, remove_me)
    i = 0
    while i < len(cleaned):
        print(len(cleaned))
        cleaned = np.delete(cleaned, remove_me)
        try:
            new_comments_list = ",".join(cleaned[0:1000])
            newcomments = get_comments(new_comments_list)
            stock_dict += get_stock_list(newcomments,stocks_list)
        except:
            continue
    stock = dict(stock_dict) 
    return stock

def make_list_of_stock_symbols():
    dataFrame = pd.read_csv("nasdaq_stocks.csv")
    symbols = dataFrame['Symbol']
    symbol_file = open('symbols', 'w')
    for symbol in symbols:
        symbol_file.write("%s\n" % symbol)
    symbol_file.close()
      
if __name__ == "__main__":

    if not (os.path.isfile(FILE_NAME)):
        make_list_of_stock_symbols()
    
    all_stocks = []

    for i in range(7): #7 is max amount
        day_to_analyze = date.today() - timedelta(days = i+3)
        
        if day_to_analyze.weekday() > 4:
            if day_to_analyze.weekday() == 6:
                continue
            else:
                day_to_analyze = date.today() - timedelta(days = i+4)               
                driver = create_driver(WEEKEND_URL)
        else:
            driver = create_driver(DAILY_URL)
        print(day_to_analyze)
        thread_id = get_comment_thread_link(driver, day_to_analyze)#Works #Gets the ID for one particular thread
        
        comment_id_dictionary = get_comment_ids(thread_id)#Works #Creates a dictionary of the comment IDs from this thread

        stocks_list = create_symbol_list() #Works #Creates a list of NASDAQ Symbols
        
        comment_id_array = np.array(comment_id_dictionary['data']) #Creates an array of all the IDs from the comment dictionary
        comment_id_list = ",".join(comment_id_array[0:1000]) #Concatenates the strings of the first 1000 comment ID's
        actual_comments = get_comments(comment_id_list)#Gets the actual comments to be analyzed
        stock_dictionary = get_stock_list(actual_comments, stocks_list)#works
       
        stocks = get_stock_count(stock_dictionary, comment_id_dictionary, stocks_list) #Purpose is to go through all the comments, not just the original 1000
        
        all_stocks.append(stocks)
    
    

    
    
    #This keeps not working due to the date going back too far, only goes to the 14th for daily discussions before it reaches
    #End of the page



#Pushshift API 60 hours behind, maybe switch to reddit api

#On command, should ask for the daily or weekly maybe monthly results
#Display a plot with the 5 most occuring stock symbols
#Display a second plot with the price of the stock during the time period

#if not(os.path.isfile('stockCounts.csv')):
#            print('creating cvs')
 ##              fieldnames = ['Stock', 'Number of Mentions']
   #             writer = csv.DictWriter(w, fieldnames=fieldnames)
    #            writer.writeheader()
     #           for stock in data:
      #              writer.writerow(stock)
       #     w.close()
        #else:
         #   print('appending file')
          #  with open('stockCounts', 'a') as a:
           #     fieldnames = ['Stock', 'Number of Mentions']
            #    writer = csv.writer(a, fieldnames = fieldnames)
             #   writer.writeheader()
              #  for stock in data:
               #     writer.writerow(stock)
            #a.close()


#while True:
 #       try:
  #          actual_comments = html_.json() #Gets the actual comments using the comment ID
   #     except Exception:
    #        continue
     #   else:
      #      break