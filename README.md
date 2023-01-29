# Cointelegraph full website scraper

Are you cryptocurrencies enthusiast? 
Are you interested in NLP and looking for a real-world news database? 
Or is it both? 
I've got you covered! 

This code scrapes all news articles from cointelegraph.com. 

The output is saved in the .csv file, and following data is stored: 
- Category of the article
- Its title
- Date and time (with timezone indication) published
- Number of views and number of shares
- Article's summary
- Article's content
- The tags, attributed to the article. 

This scrapper operates through the cointelegraph sitemap: https://cointelegraph.com/sitemap.xml and doesn't requre any input from your side.

The code doesn't use Selenium and operates through the requests library, which can be easily installed through pip: pip install requests
You will also need a BeautifulSoup library to parse the webpages (the name is beautifulsoup4, documentation is here: https://www.crummy.com/software/BeautifulSoup/bs4/doc/#installing-beautiful-soup), 
and an lxml parser. Please recall that it is highly recommended to create different environments for separate projects to manage the dependencies between libraries. 

The code takes approximately 16 hours to scrap the whole website. 

