## Pulls relevant stock symbols from the Finviz stock screener ##

#initializes empty data frame 
full_table <- data.frame(Date=as.Date(character()),
                 File=character(), 
                 User=character(), 
                 stringsAsFactors=FALSE) 

#load rvest
library(rvest)

#runs Finviz symbol scrape in a while loop.  ~496 symbols to pull
i = 1

while(i < 681){
  webpage <- paste("http://finviz.com/screener.ashx?v=111&f=geo_usa,sh_avgvol_u1000,sh_price_u5&r=",i, sep="")
  webpage <- html(webpage)

#grabs full review
  symbol <- webpage %>%
    html_nodes(".screener-link-primary") %>%
    html_text()

#puts relevant data for the current page into a data frame
  info_table <- data.frame(Symbol = symbol, stringsAsFactors=FALSE)

#combines current page data with overall data in one data frame
  full_table <-rbind(full_table,info_table)

i = i + 20
Sys.sleep(2)

}

full_table
