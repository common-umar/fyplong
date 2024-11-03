import streamlit as st
import pandas as pd
import textwrap

# Load the dataset (make sure the path is correct)
games_df = pd.read_csv('games.csv')

# Set up the title and description of the app
st.title("Game Recommendation System")
st.write("Enter a game name or a genre to get recommendations!")

# Input for game name or genre
user_input = st.text_input("Game Name or Genre", "").strip()

# Function to recommend games based on input
def recommend_games(input_value):
    # First, check if the input is a genre or a game name
    genre_recommendation = games_df[games_df['Genre'].str.contains(input_value, case=False)]
    game_recommendation = games_df[games_df['Title'].str.contains(input_value, case=False)]

    # If the input is a genre, show 5 games from that genre
    if not genre_recommendation.empty:
        st.write(f"Here are some games in the genre '{input_value}':")
        for index, row in genre_recommendation.iterrows():
            st.write(f"- {row['Title']} (Released in: {row['Released in: Japan']})")
        if len(genre_recommendation) == 0:
            st.write("No games found in this genre.")

    # If the input is a game name, show the details for that game
    elif not game_recommendation.empty:
        selected_game = game_recommendation.iloc[0]
        link = 'https://en.wikipedia.org' + selected_game['Link']
        st.write(f"Details for **{selected_game['Title']}**:")
        st.write(f"- Genre: {selected_game['Genre']}")
        st.write(f"- Developer: {selected_game['Developer']}")
        st.write(f"- Publisher: {selected_game['Publisher']}")
        st.write(f"- Released in: Japan: {selected_game['Released in: Japan']}, North America: {selected_game['North America']}, Rest of countries: {selected_game['Rest of countries']}")
        st.write(f"- Plot: {selected_game['Plots']}")
        st.write(f"[More info here]({link})")
    else:
        st.write("No games found with that name or genre.")

# When the user submits the input
if user_input:
    recommend_games(user_input)
