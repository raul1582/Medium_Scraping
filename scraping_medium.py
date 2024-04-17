import os
import sys
import requests
import re
from bs4 import BeautifulSoup

os.chdir(os.path.dirname(os.path.abspath(__file__)))

# Function to get the html of the page;
def get_page():
    url = input('Enter URL of a medium article: ')
    # handling possible error
    if not re.match(r'https?://medium.com', url):
        print('Please enter a valid website, or make sure it is a medium article')
        sys.exit(1)
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36'
    }
    res = requests.get(url, headers=headers)
    res.raise_for_status()
    soup = BeautifulSoup(res.text, 'html.parser')
    return soup, url

# function to compile all of the scraped text in one string
def collect_text(soup, url):
    fin = f'URL: {url}\n\n'
    try:
        title = soup.find('h1').text.strip()
        fin += f'Title: {title.upper()}\n'
    except AttributeError:
        title = "No Title Found"
        fin += "Title: No Title Found\n"

    article_body = soup.find('article')
    if not article_body:
        article_body = soup

    for element in article_body.find_all(['p', 'h2', 'h3', 'ul', 'ol']):
        if element.name in ['h2', 'h3']:
            fin += f'\n\n{element.text.upper()}\n'
        elif element.name in ['ul', 'ol']:
            for item in element.find_all('li'):
                fin += f'\n - {purify(item.next)}'
        else:
            fin += f'\n{purify(element.text)}'

    return fin, title

# Function to remove all the html tags and replace some with specific strings
def purify(text):
    rep = {"<br>": "\n", "<br/>": "\n", "<li>": "\n"}
    rep = dict((re.escape(k), v) for k, v in rep.items())
    pattern = re.compile("|".join(rep.keys()))
    text = pattern.sub(lambda m: rep[re.escape(m.group(0))], text)
    text = re.sub(r'\<(.*?)\>', '', text)
    return text

def save_file(fin, title):
    dir_path = './scraped_articles'
    if not os.path.exists(dir_path):
        os.mkdir(dir_path)
    file_name = '_'.join(title.split()) + '.txt'
    file_path = os.path.join(dir_path, file_name)
    with open(file_path, 'w', encoding='utf8') as file:
        file.write(fin)
    print('File Saved in directory {}'.format(file_path))

if __name__ == '__main__':
    soup, url = get_page()
    fin, title = collect_text(soup, url)
    save_file(fin, title)
