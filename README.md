# Stock-Alerts

Takes a list of stocks and sends an alert if something interesting is happening based on unusual price/volume changes and/or trading being suspended.

1. Scrapes a list of interesting stocks from the Finviz stock screener
2. Pulls data for each stock from the Yahoo Finance API every few minutes
3. Checks to see if there are any significant price and volume changes to indicate if something big or unusual is happening 
4. Pulls halt data from the NASDAQ RSS feed which could also indicate that there's something significant going on
5. Sends a text message if there's anything worth looking at
