# RedditScraper

## Table of Contents
* [Intro](#Intro)
* [Technologies](#Technologies)
* [Setup](#How-to-Install-and-Run-This-Program)
* [License](#License)

## Intro

Over the past year, a subreddit known as r/wallstreetbets has made multiple news headlines
due to the Gamestop short squeeze. Since then, the subreddit is known for targeting various
other stocks such as AMC, Blackberry, and more. 

Thus, I have created this program to scrape r/wallstreetbets and display the most frequently
mentioned stocks.

## Technologies

This project uses selenium 3.141.0, numpy 1.19.4, pandas 1.1.5, and matplotlib 3.4.2
If you do not have them installed, you can use these commands:
* 'pip install selenium'
* 'pip install pandas'
* 'pip install numpy'
* 'python -m pip install -U matplotlib'

## How to Install and Run This Program

1. Download all the dependencies
2. Navigate to where you wish to download this
3. Open command line and type 'git clone https://github.com/Steven-Jarmell/RedditScraper.git'
4. Launch the main.py folder
5. The program will display the number of comments left to go through and print out a graph at the end which will look like this  
![Figure](/Figure_1.png?raw=true)

## License

This repository is licensed under the Apache License Version 2.0