import requests
from bs4 import BeautifulSoup

url_list = {}
api_key = "df34fe1eaba7e3ba21f546924ba0fa0937e0f089"  # Not used in this example

def search_movies(query):
    movies_list = []
    search_url = f"https://1337x.to/search/{query.replace(' ', '%20')}/1/"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:92.0) Gecko/20100101 Firefox/92.0',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate, br',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1',
    }
    
    response = requests.get(search_url, headers=headers)
    
    if response.ok:
        website = BeautifulSoup(response.text, "html.parser")
        
        # Print out a snippet of the HTML to debug and ensure you are fetching the right page
        print(website.prettify()[:1000])  # Adjust this value as needed
        
        movies_table = website.find("table", class_="table-list")
        if not movies_table:
            print("No movies table found on the page.")
            return movies_list
        
        movies = movies_table.find_all("tr")[1:]  # Skip header row
        
        for index, movie in enumerate(movies):
            title_column = movie.find("td", class_="coll-1")
            if title_column:
                title_tag = title_column.find("a", class_="title")
                if title_tag:
                    title = title_tag.text.strip()
                    link = title_tag['href']
                    movie_id = f"link{index}"
                    movies_details = {
                        "id": movie_id,
                        "title": title
                    }
                    url_list[movies_details["id"]] = f"https://1337x.to{link}"
                    movies_list.append(movies_details)
    else:
        print(f"Error fetching data from 1337x.to: {response.status_code}")
    
    return movies_list
