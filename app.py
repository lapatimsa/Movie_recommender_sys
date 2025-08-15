import pickle
import streamlit as st
import requests
import difflib
import os
from dotenv import load_dotenv

load_dotenv()

def fetch_poster(movie_id):
    url = "https://api.themoviedb.org/3/movie/{}?api_key={}&language=en-US".format(movie_id, os.environ.get('MOVIE_DB_KEY'))
    data = requests.get(url)
    data = data.json()
    poster_path = data.get('poster_path')
    if poster_path:
        full_path = "https://image.tmdb.org/t/p/w500/" + poster_path
        return full_path
    return None  # Return None if there's no poster path

def recommend(movie):
    num_of_movies = 10
    if movie not in movies['original_title'].values:
        return [], []  # Return empty lists if the movie is not found
    index = movies[movies['original_title'] == movie].index[0]
    distances = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1])
    recommended_movie_names = []
    recommended_movie_posters = []
    for i in distances[0:num_of_movies]:
        movie_id = movies.iloc[i[0]].movie_id
        poster = fetch_poster(movie_id)
        if poster:  # Only append if a poster is found
            recommended_movie_posters.append(poster)
            recommended_movie_names.append(movies.iloc[i[0]]['original_title'])
    return recommended_movie_names, recommended_movie_posters

st.header('Movie Recommender System')
movies = pickle.load(open('movie_list.pkl', 'rb'))
similarity = pickle.load(open('similarity.pkl', 'rb'))

selected_movie_input = st.text_input("Type a Movie name to generate Recommendations")

if st.button('Show Recommendation'):
    try:
        # Get the closest match from the input
        selected_movie_matches = difflib.get_close_matches(selected_movie_input, movies['original_title'].tolist())
        if selected_movie_matches:
            selected_movie = selected_movie_matches[0]  # Choose the best match
            st.write(f"Showing recommendations for: **{selected_movie}**")
            if os.environ.get('MOVIE_DB_KEY') is None or os.environ.get('MOVIE_DB_KEY') == "INSERT_API_KEY_HERE":
                st.error("API key not found. Please set the API key in the .env file.")
                st.stop()
            recommended_movie_names, recommended_movie_posters = recommend(selected_movie)
            
            if recommended_movie_names:
                # Create two rows of columns with specified width
                cols1 = st.columns(5)
                for col, movie_name, movie_poster in zip(cols1, recommended_movie_names[:5], recommended_movie_posters[:5]):
                    with col:
                        st.text(movie_name)
                        st.image(movie_poster)

                cols2 = st.columns(5)
                for col, movie_name, movie_poster in zip(cols2, recommended_movie_names[5:], recommended_movie_posters[5:]):
                    with col:
                        st.text(movie_name)
                        st.image(movie_poster)
            else:
                st.error("No recommendations found. Please check the movie title.")
        else:
            st.warning("No close matches found. Please enter a valid movie title.")
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
