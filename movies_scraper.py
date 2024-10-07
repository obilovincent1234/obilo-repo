import requests
from bs4 import BeautifulSoup

url_list = {}

def search_movies(query):
    movies_list = []
    search_url = f"https://1337x.to/search/{query.replace(' ', '%20')}/1/"
    response = requests.get(search_url)
    
    if response.ok:
        website = BeautifulSoup(response.text, "html.parser")
        movies = website.find_all("tr")  # Example structure, can vary depending on site
        
        for index, movie in enumerate(movies):
            movie_name = movie.find("a", class_="title").text
            download_page = movie.find("a", href=True)["href"]
            
            movies_details = {
                "id": f"link{index}",
                "title": movie_name
            }
            url_list[movies_details["id"]] = f"https://1337x.to{download_page}"
            movies_list.append(movies_details)
    
    return movies_list


def get_movie(query):
    movie_details = {}
    
    if query in url_list:
        movie_page_link = requests.get(url_list[query]).text
        movie_page = BeautifulSoup(movie_page_link, "html.parser")
        
        title = movie_page.find("h1").text
        movie_details["title"] = title
        
        img = movie_page.find("img", class_="poster")["src"] if movie_page.find("img", class_="poster") else None
        movie_details["img"] = img
        
        download_links = movie_page.find_all("a", class_="download-link")
        final_links = {}
        
        for i, link in enumerate(download_links):
            final_links[f"Link {i+1}"] = link["href"]
        
        movie_details["links"] = final_links
    else:
        print(f"Query '{query}' not found in url_list.")
    
    return movie_details
    
