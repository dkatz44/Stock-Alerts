# -*- coding: utf-8 -*-
"""
Created on Mon Jul 11 20:03:39 2016

Stock Alerts

@author: dkatz44


symbol
AverageDailyVolume
Volume
PercentChange

"""


# Get the current time
import os # using this later
import time as tm
import pandas as pd
from urllib.parse import quote
import requests
from datetime import datetime, time
import feedparser as fd
now = datetime.now()
now_time = now.time()

# 30 second sleep to make sure internet is connected
#tm.sleep(30)

# Run from start until 4:00PM
while now_time <= time(16,00):

    # Symbol List         
    stockList = pd.read_csv('/Users/dkatz44/Desktop/StockAlerts/StockList.csv')
    
      #  print(len(stockList.index))
    
    chunkSize = len(stockList.index) / 11    
    
    reader = pd.read_table('/Users/dkatz44/Desktop/StockAlerts/StockList.csv', sep=',', chunksize=chunkSize)
    
    def apiCallByChunk(chunk):
        symbolList = str(chunk['Symbols'].tolist()).replace("[", "")
        symbolList = symbolList.replace("]", "")
        symbolList = symbolList.replace("'", "")
    
    # Get Quotes!
    
        baseURL = 'https://query.yahooapis.com/v1/public/yql?q='
    
        YQL = 'select symbol, AverageDailyVolume, Volume, PercentChange from yahoo.finance.quotes where symbol in (' + symbolList + ')'
    
        yahooString = '&format=json&diagnostics=false&env=store%3A%2F%2Fdatatables.org%2Falltableswithkeys&callback='
    
        encodedYQL = quote(YQL)
    
        query = baseURL + encodedYQL + yahooString
    
    # Send the query
        try:
            resp = requests.get(query)
            
        except requests.exceptions.ConnectionError as e:
            pass
        # e.args
        # e.args[0]
        # dir(e.args[0])
        # e.args[0].reason
        if resp != None:
            jsonResults = resp.json()
        #resp = requests.get("https://query.yahooapis.com/v1/public/yql?q=select%20*%20from%20yahoo.finance.quotes%20where%20symbol%20in%20(%22YHOO%22%2C%22AAPL%22%2C%22GOOG%22%2C%22MSFT%22)&diagnostics=true&env=store%3A%2F%2Fdatatables.org%2Falltableswithkeys")        
        tm.sleep(2)
        #tm.sleep(2)
        return jsonResults['query']['results']


    stockList = []    
    
    for chunk in reader:
        stockList.append(apiCallByChunk(chunk))

    
    if len(stockList) > 0:   
                       
        combinedData = pd.io.json.json_normalize(stockList, 'quote')
        
        combinedData = combinedData.dropna()

        combinedData['PercentChange'] = combinedData['PercentChange'].map(lambda x: float(str(x).strip('%')) / 100)
    
        combinedData['AverageDailyVolume'] = combinedData['AverageDailyVolume'].map(int)
    
        combinedData['Volume'] = combinedData['Volume'].map(int)

        combinedData['volDiffPercent'] = combinedData['Volume'] / combinedData['AverageDailyVolume']
    
        combinedData = combinedData[(combinedData['volDiffPercent'] > 1) & (combinedData['PercentChange'] > 0)]

    if len(combinedData.index) > 0:
    # Sort by volDiffPercent and percentChange
        combinedData = combinedData.sort_values(['volDiffPercent', 'PercentChange'], ascending=[False, False])
    
    # Reset the index with the new sorted order
        combinedData = combinedData.reset_index(drop=True)
    
    # Convert percentChange and volDiffPercent into formatted strings
        combinedData['PercentChange'] = combinedData['PercentChange'].apply(lambda x: str("{:0.1%}".format(x)))
        combinedData['volDiffPercent'] = combinedData['volDiffPercent'].apply(lambda x: str("{:0.0%}".format(x)))
    
    # Create a formatted column with all of the data
        combinedData['combined'] = \
              combinedData['symbol'] + \
              ' ' + combinedData['PercentChange'] + \
              ' ' + combinedData['volDiffPercent'] + '\n'
    
    # Create the watchList by getting the combined column from the combinedData DataFrame
        watchList = combinedData['combined'].tolist()
  
# Create the text message

# Add the top 15 stocks by volDiffPercent to the text
        formattedWatchList = ''

        for x in range(len(watchList)): 
            if x <= 15:
                formattedWatchList += watchList[x]
            else: 
                    break

    else:
        formattedWatchList = 'No Stocks Match \n'

    text = '"' + formattedWatchList + '"'

# Insert the text into an AppleScript command (don't send blank texts)
    if len(formattedWatchList) > 0:
        cmd = "osascript<<END\n"
        cmd = cmd + """tell application "Messages" \n"""
        cmd = cmd + "activate --steal focus \n"
        cmd = cmd + "send " + text
        cmd = cmd + """ to buddy "dkatz44@gmail.com" of (service 1 whose service type is iMessage) \n"""
        cmd = cmd + "end tell\n" 
        cmd = cmd + "END"

# Embed the command in a function
        def send_text():
            os.system(cmd)

# Send the text!
        send_text()

    now = datetime.now()
    now_time = now.time()  
    print("Stock Loop Completed:", now_time)
    
# Stock Halts RSS Feed
        
# Halt Code Definitions
    def halt_code_lookup(argument):
        switcher = {
            'T1': "News Pending",
            'T2': "News Released",
            'T3': "News and Resumption Times",
            'T5': 'Single Stock Trading Pause in Effect',
            'T6': 'Extraordinary Market Activity',
            'T7': 'Single Stock Trading Pause/Quotation-Only Period',
            'T8': 'Exchange-Traded-Fund (ETF)',
            'T12': 'Info Requested by NASDAQ',
            'H4': 'Non-Nompliance',
            'H9': 'Not Current',
            'H10': 'SEC Trading Suspension',
            'H11': 'Regulatory Concern',
            'O1': 'Operations Halt',
            'IPO1': 'HIPO Issue not yet Trading',
            'M1': 'Corporate Action',
            'M2': 'Quotation Not Available',
            'LUDP': 'Volatility Trading Pause',
            'LUDS': 'Volatility Trading Pause - Straddle Condition',
            'MWC1': 'Market Wide Circuit Breaker Halt - Level 1',
            'MWC2': 'Market Wide Circuit Breaker Halt - Level 2',
            'MWC3': 'Market Wide Circuit Breaker Halt - Level 3',
            'MWC0': 'Market Wide Circuit Breaker Halt - Carry over',
            'R4':	'Qualifications Issues Resolved',
            'R9':	'Filing Requirements Satisfied',
            'C3':	'News Not Forthcoming; Trading To Resume',
            'C4':	'Halt Ended; maint. req. met; Resume',
            'C9':	'Halt Concluded; Filings Met; Resume',
            'C11':	'Halt Concluded By Other Regulatory Auth,; Resume',
            'R1':	'New Issue Available',
            'R2':	'Issue Available',
            'IPOQ':	'IPO security released for quotation',
            'IPOE':	'IPO security - positioning window extension',
            'MWCQ':	'Market Wide Circuit Breaker Resumption',
            'M':	'Volatility Trading Pause',
            'D':	'Security Deletion',
            ' ':    'Reason Not Available'    
            }
        return switcher.get(argument)
    
    tm.sleep(5)

# Get The RSS Feed

    haltFeed = fd.parse('http://www.nasdaqtrader.com/rss.aspx?feed=tradehalts')    
    
# Issue Symbol
# Halt Time
# Reason
    haltList = ''
    
    if haltFeed['entries'] != None:
        if len(haltFeed['entries']) > 0:
    
            for x in range(len(haltFeed['entries'])):
                
                # Format Halt Time
                haltTime = datetime.strptime(haltFeed['entries'][x]['ndaq_halttime'], '%H:%M:%S').time()
            
                haltHour = haltTime.hour 
                haltMin = haltTime.minute

                haltTime = datetime.strptime(str(haltHour) + ':' + str(haltMin), '%H:%M')                
                
                # Append halts to haltList
                haltList += str(haltFeed['entries'][x]['ndaq_issuesymbol'] + ' ' + \
                str(datetime.strftime(haltTime, '%I:%M %p')) + ' ' + \
                halt_code_lookup(haltFeed['entries'][x]['ndaq_reasoncode']) + '\n')
    
            haltText = '"' + haltList + '"' 

# Insert the text into an AppleScript command (don't send blank texts)
    if len(haltList) > 0:
        cmd = "osascript<<END\n"
        cmd = cmd + """tell application "Messages" \n"""
        cmd = cmd + "activate --steal focus \n"
        cmd = cmd + "send " + haltText
        cmd = cmd + """ to buddy "dkatz44@gmail.com" of (service 1 whose service type is iMessage) \n"""
        cmd = cmd + "end tell\n" 
        cmd = cmd + "END"

# Embed the command in a function
        def send_haltText():
            os.system(cmd)

# Send the text!
        send_haltText()

    now = datetime.now()
    now_time = now.time()  
    print("Halt Loop Completed:", now_time) 
 
# Sleep for 5 minutes
    tm.sleep(300)
    
# Update the time variable
    now = datetime.now()
    now_time = now.time()
    print("Loop starting:", now_time)
#    print(now.time())
#    break

cmd = "osascript<<END\n"
cmd = cmd + """tell application "Messages" \n"""
cmd = cmd + "quit\n"
cmd = cmd + "end tell\n" 
cmd = cmd + "END"    

def quit_msgs():
    os.system(cmd)

quit_msgs()
print("Program Ended")

#cmd = """osascript<<END
#tell application "Messages"
#   send "test" to buddy "+18609787397" of service "SMS"
#end tell
#END"""

#def send_text():
#     os.system(cmd)
     
#send_text()


"""

watchList = []
summaryString = ''

for x in resp.json()['query']['results']['quote']:

    vol = int(x['Volume'])
    dailyVol = int(x['AverageDailyVolume'])    
    
    volDiffPercent = vol / dailyVol    

    percentChange = float(x['PercentChange'].strip('%'))/100
    
    if volDiffPercent > 1 and percentChange > 0:
        
        symbol = x['symbol']
#        change = x['Change']
        percentChange = str("{:0.1%}".format(percentChange))
 #       volume = str(format(vol, ',d'))
 #       averageDailyVolume = str(format(dailyVol, ',d'))
        volDiffPercentString = str("{:0.0%}".format(volDiffPercent))
        
        summaryString = str(symbol + ' ' + percentChange + ' ' + volDiffPercentString + '\n') 
        
        watchList.append(summaryString)
        
#print("{:0.0%}".format(volChangePercent))  
#print("{:0.2%}".format(percentChange))    
#change = resp.json()['query']['results']['quote'][0]['Change']
#symbol = resp.json()['query']['results']['quote'][0]['symbol']
  
      
# Sort through the data by populating lists for each symbol that meets the 
# volDiffPercent and percentChange criteria
    symbolArray = []
    percentChangeArray = []
    volDiffPercentArray = []

    for x in resp.json()['query']['results']['quote']:
        if x['PercentChange'] is not None:
            vol = int(x['Volume'])
            dailyVol = int(x['AverageDailyVolume'])    
    
            volDiffPercent = vol / dailyVol    
            
            percentChange = float(x['PercentChange'].strip('%'))/100
    
            if volDiffPercent > 1 and percentChange > 0:
        
                symbolArray.append(x['symbol'])
                percentChangeArray.append(float(x['PercentChange'].strip('%'))/100) # get percentChange as a float
                volDiffPercentArray.append(round(int(x['Volume']) / int(x['AverageDailyVolume']),2)) # get volDiffPercent as a rounded int (important for sorting)

# Create a DataFrame with symbol, percentChange, and volDiffPercent
    if len(symbolArray) > 0:

        combinedData = pd.DataFrame(
        {'symbol' : symbolArray,
         'percentChange' : percentChangeArray,
         'volDiffPercent' : volDiffPercentArray
         })

# Sort by volDiffPercent and percentChange
        combinedData = combinedData.sort_values(['volDiffPercent', 'percentChange'], ascending=[False, False])

# Reset the index with the new sorted order
        combinedData = combinedData.reset_index(drop=True)

# Convert percentChange and volDiffPercent into formatted strings
        combinedData['percentChange'] = combinedData['percentChange'].apply(lambda x: str("{:0.1%}".format(x)))
        combinedData['volDiffPercent'] = combinedData['volDiffPercent'].apply(lambda x: str("{:0.0%}".format(x)))

# Create a formatted column with all of the data
        combinedData['combined'] = \
              combinedData['symbol'] + \
              ' ' + combinedData['percentChange'] + \
              ' ' + combinedData['volDiffPercent'] + '\n'

# Create the watchList by getting the combined column from the combinedData DataFrame
        watchList = combinedData['combined'].tolist()
  
      
"""
