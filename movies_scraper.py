import requests
from bs4 import BeautifulSoup

# URL of the page you want to scrape
url = 'https://1337x.to/'

# Send a request to the website
response = requests.get(url)

# Parse the HTML content
soup = BeautifulSoup(response.text, 'html.parser')

# Find movie elements (adjust the selector based on the website structure)
movies = soup.find_all('div', class_='box-info')  # Example class name

for movie in movies:
    title = movie.find('a').text  # Example: Title in an <a> tag
    download_url = movie.find('a', text='Download')['href']  # Find download link

    print(f'Title: {title}, Download URL: {download_url}')
