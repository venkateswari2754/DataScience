# -*- coding: utf-8 -*-
"""movierecommended.py

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1cfaP04WQ4fj5GleZWP8eMLj7s6fZWx6q
"""

import numpy as np
import pandas as pd
import ast
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import pickle
import nltk
from nltk.stem.porter import PorterStemmer
import requests


# Convert 'genres' and 'keywords' to lists of strings
def convert(obj):
    list_ = []
    for i in ast.literal_eval(obj):
        list_.append(i['name'])
    return list_

# Extract top 3 cast members
def get_top_three(obj):
    list_ = []
    counter = 0
    for i in ast.literal_eval(obj):
        if counter != 3:
            list_.append(i['name'])
            counter += 1
        else:
            break
    return list_

# Extract director from 'crew'
def fetch_director(crew_data):
    directorlist_ = []
    crew_list = ast.literal_eval(crew_data)
    for crew_member in crew_list:
        if crew_member.get('job') == 'Director':
            directorlist_.append(crew_member.get('name'))
    return directorlist_

#Stemming function
ps=PorterStemmer()
def stem(text):
  y=[]
  for i in text.split():
    y.append(ps.stem(i))
  return " ".join(y)


# Load the movies and credits data
movies = pd.read_csv('/content/sample_data/tmdb_5000_credits.csv')
credits = pd.read_csv('/content/sample_data/tmdb_5000_movies.csv')

# Merge the two DataFrames
movies = movies.merge(credits, on='title')

# Select the desired columns
movies = movies[['movie_id', 'title', 'overview', 'genres', 'keywords', 'cast', 'crew']]

# Handle missing values and duplicates
movies.dropna(inplace=True)
movies.drop_duplicates(inplace=True)

movies['genres'] = movies['genres'].apply(convert)
movies['keywords'] = movies['keywords'].apply(convert)

#get top three
movies['cast'] = movies['cast'].apply(get_top_three)

#fetch only directors
movies['crew'] = movies['crew'].apply(fetch_director)

# Convert 'overview' to list of words
movies['overview'] = movies['overview'].apply(lambda x: x.split())

# Remove spaces from 'genres', 'keywords', 'cast', and 'crew'
movies['genres'] = movies['genres'].apply(lambda x: [i.replace(" ", "") for i in x])
movies['keywords'] = movies['keywords'].apply(lambda x: [i.replace(" ", "") for i in x])
movies['cast'] = movies['cast'].apply(lambda x: [i.replace(" ", "") for i in x])
movies['crew'] = movies['crew'].apply(lambda x: [i.replace(" ", "") for i in x])

#concat all the columns into one tag
movies['tags'] = movies['overview'] + movies['genres'] + movies['keywords'] + movies['cast'] + movies['crew']

#create new dataframe
new_df = movies[['movie_id', 'title', 'tags']]

# Convert tags into string and each list should concat with space
new_df['tags'] = new_df['tags'].apply(lambda x: " ".join(x))

# Convert tags into lowercase
new_df['tags'] = new_df['tags'].apply(lambda x: x.lower())

#let's implement vectorization. The user provide movie based on that 5 similar movies should be provided
cv=CountVectorizer(max_features=5000,stop_words='english')

#sykit send the data in the form of matrix, need to convert into numpy array
vectors=cv.fit_transform(new_df['tags']).toarray()

# apply stemming as to substitue same words like loved, loving, love
new_df['tags']=new_df['tags'].apply(stem)

#Let's caliculate the distance between the movies. if distance is more similarity will be more.
#it shows similarity with other movies
similarity=cosine_similarity(vectors)

def recommend(movie):
    # Convert movie title to lowercase for case-insensitive matching
    movie = movie.lower()
    movie_index = new_df[new_df['title'].str.lower() == movie].index
    if len(movie_index) > 0:  # Check if any matching movies were found
        movie_index = movie_index[0]
        distances = similarity[movie_index]
        movies_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]
        recommended_movies_poster = []
        recommended_movies = []
        for i in movies_list:
            recommended_movies.append(new_df.iloc[i[0]].title)
            recommended_movies_poster.append(new_df.iloc[i[0]].movie_id)
        return recommended_movies,recommended_movies_poster
    else:
        return "Movie not found in the dataset." #Return a message if movie is not found

def fetch_poster(movie_id):
    response = requests.get('https://api.themoviedb.org/3/movie/{}?api_key=8265&language=en-US'.format(movie_id))
    data = response.json()
    return "https://image.tmdb.org/t/p/w500/" + data['poster_path']

recommend('avatar')

import pickle
pickle.dump(new_df,open('movies.pkl','wb'))

!pip install streamlit

!apt-get install ffmpeg

!pip install pyngrok

# Commented out IPython magic to ensure Python compatibility.
# %%writefile app.py
# import streamlit as st
# import pickle
# st.title('Movie Recommender System')
# movies_list=pickle.load(open('movies.pkl','rb'))
# movies_list=movies_list['title'].values
# selected_movie=st.selectbox(
#     "Type or select a movie from the dropdown",
#     movies_list
# )
# if st.button('Show Recommendation'):
#   names,poster=recommend(selected_movie)
#   col1,col2,col3,col4,col5=st.columns(5)
#   with col1:
#     st.text(names[0])
#     st.image(fetch_poster(poster[0]))
#   with col2:
#     st.text(names[1])
#     st.image(fetch_poster(poster[1]))
#   with col3:
#     st.text(names[2])
#     st.image(fetch_poster(poster[2]))
#   with col4:
#     st.text(names[3])
#     st.image(fetch_poster(poster[3]))
#   with col5:
#     st.text(names[4])
#     st.image(fetch_poster(poster[4]))

!streamlit run app.py