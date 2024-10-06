import requests
from bs4 import BeautifulSoup

url_list = {}
api_key = "df34fe1eaba7e3ba21f546924ba0fa0937e0f089"

def search_movies(query):
    movies_list = []
    website = BeautifulSoup(requests.get(f"https://185.53.88.104/?s={query.replace(' ', '+')}").text, "html.parser")
    movies = website.find_all("a", {'class': 'ml-mask jt'})
    
    for index, movie in enumerate(movies):  # Use enumerate for unique IDs
        if movie:
            movies_details = {
                "id": f"link{index}",
                "title": movie.find("span", {'class': 'mli-info'}).text if movie.find("span", {'class': 'mli-info'}) else "Unknown Title"
            }
            url_list[movies_details["id"]] = movie['href']
            movies_list.append(movies_details)
    
    return movies_list


def get_movie(query):
    movie_details = {}
    
    if query in url_list:  # Check if query exists in url_list
        movie_page_link = BeautifulSoup(requests.get(url_list[query]).text, "html.parser")
        
        if movie_page_link:
            title = movie_page_link.find("div", {'class': 'mvic-desc'}).h3.text if movie_page_link.find("div", {'class': 'mvic-desc'}) else "Unknown Title"
            movie_details["title"] = title
            
            img = movie_page_link.find("div", {'class': 'mvic-thumb'})['data-bg'] if movie_page_link.find("div", {'class': 'mvic-thumb'}) else None
            movie_details["img"] = img
            
            links = movie_page_link.find_all("a", {'rel': 'noopener', 'data-wpel-link': 'internal'})
            final_links = {}
            for i in links:
                url = f"https://urlshortx.com/api?api={api_key}&url={i['href']}"
                response = requests.get(url)
                
                if response.ok:  # Check if response is OK
                    link = response.json()
                    final_links[i.text] = link.get('shortenedUrl', "Shortened URL not available")
            
            movie_details["links"] = final_links
            
    else:
        print(f"Query '{query}' not found in url_list.")

    return movie_details
    
