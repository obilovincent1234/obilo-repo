from bs4 import BeautifulSoup
import requests

def search_movies(query):
    movies_list = []
    url_list = {}  # Add this back if it's part of your original design

    search_url = f"https://185.53.88.104/?s={query.replace(' ', '+')}"
    print(f"Searching movies at: {search_url}")  # Debugging line
    
    response = requests.get(search_url)
    print(f"Status Code: {response.status_code}")  # Check if request is successful

    if response.status_code == 200:
        website = BeautifulSoup(response.text, "html.parser")
        movies = website.find_all("a", {'class': 'ml-mask jt'})
        
        if not movies:
            print("No movies found!")  # Debugging line
        
        for index, movie in enumerate(movies):  # Use enumerate for unique IDs
            if movie:
                title_element = movie.find("span", {'class': 'mli-info'})
                title = title_element.text if title_element else "Unknown Title"
                movie_details = {
                    "id": f"link{index}",
                    "title": title
                }
                url_list[movie_details["id"]] = movie['href']
                movies_list.append(movie_details)
                
        print(f"Movies List: {movies_list}")  # Debugging line
    
    else:
        print(f"Failed to retrieve the search results. Status code: {response.status_code}")

    return movies_list
    
