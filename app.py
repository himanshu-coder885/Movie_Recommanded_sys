import streamlit as stl
import pickle
import pandas as pd
import requests

# Use the API key provided
OMDB_API_KEY = "b19aa4c6"
PLACEHOLDER_URL = "https://placehold.co/500x750?text=No+Poster"

# --- CACHED POSTER FETCHING using www.omdbapi.com (JSON Endpoint) ---
@stl.cache_data(show_spinner=False)
def fetch_poster(movie_id):
    """
    Fetches the actual public poster URL from the reliable JSON Data API.
    This public URL is what your browser should load without issues.
    """
    if not movie_id or (isinstance(movie_id, str) and movie_id.upper() == 'N/A'):
        return PLACEHOLDER_URL

    # Use the Data API to get the JSON object
    url = f"http://www.omdbapi.com/?i={movie_id}&apikey={OMDB_API_KEY}"
    
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()
        
        if data.get('Response') == 'True':
            poster = data.get('Poster')
            if poster and poster != "N/A":
                # Returns a public URL like https://m.media-amazon.com/...
                return poster 
        
    except requests.exceptions.RequestException as e:
        # stl.warning(f"Request failed for ID {movie_id}: {e}") # Debugging
        pass 
        
    # If API fails or no poster found, return placeholder
    return PLACEHOLDER_URL


def recommend(movie):
    if movie not in new_df['title'].values:
        return [], []
        
    movie_index = new_df[new_df['title'] == movie].index[0]
    distances = similarity[movie_index]
    movies_list = sorted(list(enumerate(distances)),
                         reverse=True,
                         key=lambda x: x[1])[1:6]
    
    recommend_movies = []
    recommend_movies_posters = []
    
    for i in movies_list:
        idx = i[0]
        movie_row = new_df.iloc[idx]
        
        movie_id = movie_row.get('movies_id')
        
        recommend_movies.append(movie_row['title'])
        # Call the CACHED function to get the public poster URL
        recommend_movies_posters.append(fetch_poster(movie_id))

    return recommend_movies, recommend_movies_posters    

# --- Data Loading ---
try:
    new_df = pickle.load(open('movies.pkl','rb'))  
    movies_list = new_df['title'].values
    similarity = pickle.load(open('similarity.pkl','rb'))
except FileNotFoundError:
    stl.error("Error: movie or similarity pickle files not found.")
    stl.stop()

# --- Streamlit UI ---
stl.title('Movie Recommendation System')

select_movie_name = stl.selectbox(
    'Select a Movie',
    movies_list
)

if stl.button('Recommend'):
    names, posters = recommend(select_movie_name)
    
    cols = stl.columns(5)
    
    for i in range(len(names)):
        with cols[i]:
            stl.text(names[i])
            
            poster_url = posters[i] 
            
            try:
                # stl.image now loads a simple, public Amazon/media URL, NOT the restricted OMDB image endpoint.
                stl.image(poster_url, use_container_width=True)
            except Exception:
                stl.image(PLACEHOLDER_URL, use_container_width=True)