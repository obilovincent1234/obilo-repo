import requests
from bs4 import BeautifulSoup
from urllib.parse import quote_plus  # For encoding search queries

url_list = {}
api_key = "df34fe1eaba7e3ba21f546924ba0fa0937e0f089"  # Not used in this example

def search_movies(query):
    movies_list = []
    search_url = f"https://1337x.to/search/{quote_plus(query)}/1/"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
    }
    
    # Make the request
    response = requests.get(search_url, headers=headers)
    
    if response.ok:
        website = BeautifulSoup(response.text, "html.parser")
        
        # Debugging: Print the response to check if it's the right HTML
        print("Received HTML: ", website.prettify()[:500])  # Only print first 500 chars to avoid clutter
        
        # Find the table with search results
        movies_table = website.find("table", class_="table-list")
        if not movies_table:
            print("No movies table found on the page.")
            return movies_list
        
        # Get all movie rows, skipping the header
        movies = movies_table.find_all("tr")[1:]
        
        if not movies:
            print("No movie entries found on the page.")
        
        # Loop through the movies found
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
                    print(f"No title found for movie at index {index}")
            else:
                print(f"No title column found for movie at index {index}")
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
            movie_details["title"] = title_tag.text.strip() if title_tag else "Unknown Title"
            
            # Extract image
            img_tag = movie_page.find("div", class_="movie-image").find("img")
            movie_details["img"] = img_tag["src"] if img_tag else None
            
            # Extract download links
            download_section = movie_page.find("div", class_="download-links")
            final_links = {}
            if download_section:
                download_links = download_section.find_all("a", class_="button")
                for i, link in enumerate(download_links):
                    download_url = link['href']
                    final_links[f"Download Link {i+1}"] = download_url
            movie_details["links"] = final_links
        else:
            print(f"Error fetching movie details from 1337x.to: {response.status_code}")
    else:
        print(f"Query '{query}' not found in url_list.")
    
    return movie_details
    
