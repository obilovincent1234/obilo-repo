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

def get_movie(query):
    movie_details = {}
    
    if query in url_list:
        movie_page_url = url_list[query]
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
        }
        response = requests.get(movie_page_url, headers=headers)
        
        if response.ok:
            movie_page = BeautifulSoup(response.text, "html.parser")
            
            # Extract title
            title_tag = movie_page.find("h1", class_="movie-info-title")
            if title_tag:
                movie_details["title"] = title_tag.text.strip()
            else:
                movie_details["title"] = "Unknown Title"
            
            # Extract image
            img_tag = movie_page.find("div", class_="movie-image").find("img")
            if img_tag and img_tag.get("src"):
                movie_details["img"] = img_tag["src"]
            else:
                movie_details["img"] = None
            
            # Extract download links
            download_section = movie_page.find("div", class_="download-links")
            if download_section:
                download_links = download_section.find_all("a", class_="button")
                final_links = {}
                for i, link in enumerate(download_links):
                    download_url = link['href']
                    final_links[f"Download Link {i+1}"] = download_url
                movie_details["links"] = final_links
            else:
                movie_details["links"] = {}
        else:
            print(f"Error fetching movie details from 1337x.to: {response.status_code}")
    else:
        print(f"Query '{query}' not found in url_list.")
    
    return movie_details
            
