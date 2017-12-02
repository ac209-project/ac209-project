"""
Saves DataFrame containing celebrity information scraped from usmagazine.com.
"""

from bs4 import BeautifulSoup
import pandas as pd
import requests

SAVE_PATH = '../celebs.csv'

df = pd.DataFrame(columns=['name', 'url'])

#####################################################################

# Make HTTP request more human-like.
__HEADERS = {
    'User-Agent':"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_5) AppleWebKit "
                 "537.36 (KHTML, like Gecko) Chrome",
    'Accept':"text/html, application/xhtml+xml, application/xml;q=0.9, "
             "image/webp,"
             "*/*;q=0.8"}


def get_soup (url, parser='html.parser'):
    """Init BeautifulSoup tag from HTML located at a given url."""
    http_req = requests.get(url, headers=__HEADERS)
    return BeautifulSoup(http_req.text, parser)


def create_row (tag):
    """Creates row for DataFrame from <li> tag."""
    name = tag.find('span', {'class':'celebrity-name'}).text
    url = tag.find('a')['href']
    return {'name':name, 'url':url}


#####################################################################

# Even though link is for the 'a' section, all celebs contained on the page.
soup = get_soup('https://www.usmagazine.com/celebrities/a/')

celeb_listings = soup.find(
      'div', {'class':'celebrity-body-content'}).find(
      'ul', {'class':'celebrity-listing'}).find_all('li')

for celeb_listing in celeb_listings:
    new_row = create_row(celeb_listing)
    df = df.append(new_row, ignore_index=True)

df.set_index('name', inplace=True, drop=True)
df.to_csv(SAVE_PATH)

print('Finished saving celebs DataFrame to {}'.format(SAVE_PATH))
