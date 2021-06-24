from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from collections import Counter
import requests
import os.path
import numpy as np
from datetime import date, timedelta
from dateutil.parser import parse
import pandas as pd
import matplotlib.pyplot as plt

DAILY_URL = "https://www.reddit.com/r/wallstreetbets/search/?q=flair%3A%22Daily%20Discussion%22&restrict_sr=1&sort=new"
WEEKEND_URL = "https://www.reddit.com/r/wallstreetbets/search/?q=flair%3A%22Weekend%20Discussion%22&restrict_sr=1&sort="
FILE_NAME = "symbols.txt"


def create_driver(URL):
    PATH = "C:\Program Files (x86)\chromedriver.exe" # Sets up the path for the driver
    chrome_options = Options() # Adds options in order to disable the notification that would pop up
    chrome_options.add_argument("--disable-notifications")
    driver = webdriver.Chrome(options=chrome_options, executable_path = PATH) # Creates the driver
    driver.get(URL) # Gets either the daily url or weekend url
    return driver

def get_comment_thread_link(driver, day_to_analyze):

    thread_links = driver.find_elements_by_xpath('//*[@class= "_eYtD2XCVieq6emjKBH3m"]') # Find the element which is the discussion header

    for link in thread_links:                                                            # Class is the same whether it is daily or weekend
        if link.text.startswith('Daily Discussion Thread'): # If the thread is daily discussion it gets the link for the post
            date = "".join(link.text.split(' ')[-3:]) # Splits the link, only grabbing the date in the header
            parsed = parse(date) # Parses the date in order for comparison
            if parse(str(day_to_analyze)) == parsed:
                thread_link = link.find_element_by_xpath('../..').get_attribute('href') # Gets the link for the thread to be analyzed
                            
        if link.text.startswith('Weekend'): #If the thread is a weekend discussion it gets the link
            date = "".join(link.text.split(' ')[-3:])             
            parsed = parse(date)
            if parse(str(day_to_analyze)) == parsed:
                thread_link = link.find_element_by_xpath('../..').get_attribute('href')
        
    thread_id = thread_link.split('/')[6] # Cuts the thread link to only grab the ID for the thread
    driver.close() # Closes the driver, as it is now unneeded
    return thread_id   

def get_comment_ids(thread_id):
    html = requests.get(f'https://api.pushshift.io/reddit/submission/comment_ids/{thread_id}') # Uses the pushshift API to get individual comment IDs
    comment_id_list = html.json() # Gets a json version of the comment ID
    return comment_id_list

def create_symbol_list():
    with open("symbols", "r") as file: # Opens the symbols file
        stock_symbols = file.readlines() # Reads the file
        symbol_list = [] # Creates a list which will contain the symbols
        for symbol in stock_symbols:
            symbol = symbol.replace('\n', '') # Gets rid of the separation inside the text file, and uts the symbols side by side separated by a comma
            symbol_list.append(symbol) # Puts the symbols in the list
    return symbol_list

def get_comments(comment_list):
    return requests.get(f'https://api.pushshift.io/reddit/comment/search?ids={comment_list}&fields=body&size=1000').json() # Pushshift API request for the comment threads
    
def get_stock_list(actual_comments, stocks_list):
    stock_dict = Counter() # Creates a container to keep track of how many times the stock tickers are mentioned
    for comment in actual_comments['data']:
        for stock in stocks_list:
            if stock in comment['body']: # If the stock ticker is mentioned in the comment thread, it gets added to the container
                stock_dict[stock] += 1
    return stock_dict

def get_stock_count(stock_dict, comments_list, stocks_list):
    orig_list = np.array(comments_list['data']) # Creates an array of all the comments
    remove_me = slice(0,1000) # Initializes the number of comments to be removed since pushshift API only allows for 1000 requests
    cleaned = np.delete(orig_list, remove_me) # Uses the remove_me to delete 1000 comments so they are not repeated
    i = 0
    while i < len(cleaned): # While there are still comments left the loop continues
        print(len(cleaned)) # Prints the number of comments left to let the user know
        cleaned = np.delete(cleaned, remove_me) 
        try:
            new_comments_list = ",".join(cleaned[0:1000])
            newcomments = get_comments(new_comments_list) # This loop will throw a "Expecting value: line 1 column 1 (char 0)" exception
            stock_dict += get_stock_list(newcomments,stocks_list) # I believe this is due to symbols or some unknown character in reddit comments
        except: # Skips over the block of comments that causes the problem to continue the program
            continue
    
    return stock_dict

def make_list_of_stock_symbols(): # Simply creates a file of stock tickers
    dataFrame = pd.read_csv("nasdaq_stocks.csv")
    symbols = dataFrame['Symbol']
    symbol_file = open('symbols', 'w')
    for symbol in symbols:
        symbol_file.write("%s\n" % symbol)
    symbol_file.close()
      
if __name__ == "__main__":

    if not (os.path.isfile(FILE_NAME)): # If the user does not have the stock ticker file, this creates it
        make_list_of_stock_symbols()
    
    all_stocks = [] 
    datesMentioned = []

    for i in range(7):
        day_to_analyze = date.today() - timedelta(days = i+3) # Pushshift API is ~60 hours behind so this starts the program 3 days back
        
        if day_to_analyze.weekday() > 4:
            if day_to_analyze.weekday() == 6: # Sundays do not have posts so they are skipped
                continue
            else:
                day_to_analyze = date.today() - timedelta(days = i+4) # If the day to be analyzed is a saturday, it opens               
                driver = create_driver(WEEKEND_URL)                   # A weekend driver to Friday when the Weekend discussion
        else:                                                         # Post is created
            driver = create_driver(DAILY_URL)
        
        datesMentioned.append(day_to_analyze) # Adds to the dates list for future use

        thread_id = get_comment_thread_link(driver, day_to_analyze) # Gets the ID for one particular thread
        
        comment_id_dictionary = get_comment_ids(thread_id) # Creates a dictionary of the comment IDs from this thread

        stocks_list = create_symbol_list() # Creates a list of NASDAQ Symbols
        
        comment_id_array = np.array(comment_id_dictionary['data']) # Creates an array of all the IDs from the comment dictionary
        comment_id_list = ",".join(comment_id_array[0:1000]) # Concatenates the strings of the first 1000 comment ID's

        try:
            actual_comments = get_comments(comment_id_list) # Gets the actual comments to be analyzed
        except:  
            continue 
                     
        # Had to put this statement in a try except loop since sometimes the comments 
        # Throw a JSONDecodeError, which crashes the program
        # From stackoverflow, this error could be from 3 reasons:
        # XML/HTML output 
        # non-JSON conforming quoting
        # incompatible character encoding
        # I believe that some of the comments contain certain characters which throw the JSONDecodeError

        stock_dictionary = get_stock_list(actual_comments, stocks_list)
       
        stocks = get_stock_count(stock_dictionary, comment_id_dictionary, stocks_list) # Purpose is to go through all the comments, not just the original 1000
        
        all_stocks.append(stocks)
    
    combinedDataFrame = pd.DataFrame() # Creates an empty dataframe which the others will be combined into

    for stock in all_stocks: # Combines all the dictionaries into one dataframe
        df = pd.DataFrame(stock, index=[0])
        combinedDataFrame = pd.concat([combinedDataFrame, df], axis=1)

    combinedDataFrame = (pd.melt(combinedDataFrame) 
    .rename(columns={ 
    'variable' : 'Stock Ticker',
    'value' : 'Number of Occurences'}))

    aggregation_functions = {'Stock Ticker': 'first' , 'Number of Occurences': 'sum'}
    combinedDataFrame = combinedDataFrame.groupby('Stock Ticker', as_index=False).agg(aggregation_functions) # Aggregates the stock tickers 
    highestOccuring = combinedDataFrame.sort_values('Number of Occurences', ascending = False).head()

    plt.bar(highestOccuring['Stock Ticker'], highestOccuring['Number of Occurences'])
    plt.title('Most Common Stock Tickers Mentioned from ' + str(datesMentioned[-1]) + ' to ' + str(datesMentioned[0]))
    plt.xlabel('Stock Tickers') # Uses matplotlib to print a bar graph of the top 5 most mentioned stocks
    plt.ylabel('Number of Mentions')
    plt.show()