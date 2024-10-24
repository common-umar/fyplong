import streamlit as st
import pandas as pd
import textwrap
from urllib.parse import unquote  # For proper URL decoding

# Load and Cache the data
@st.cache_data(persist=True)
def getdata():
    games_df = pd.read_csv('Games_dataset.csv', index_col=0)
    similarity_df = pd.read_csv('sim_matrix.csv', index_col=0)
    return games_df, similarity_df

games_df, similarity_df = getdata()

# Sidebar
st.sidebar.markdown('<strong><span style="color: #8B2500;font-size: 26px;"> Game recommendation</span></strong>', unsafe_allow_html=True)
st.sidebar.markdown('An app by [Long Do](https://doophilong.github.io/Portfolio/)')
st.sidebar.image('pexels-pixabay-275033.jpg', use_column_width=True)
st.sidebar.markdown('<strong><span style="color: #EE4000;font-size: 26px;">:slot_machine: Choose your game !!!</span></strong>', unsafe_allow_html=True)
ph = st.sidebar.empty()

# Fetch game from URL query parameters and decode it
query_params = st.experimental_get_query_params()
default_game = unquote(query_params.get('game', [''])[0])  # Decode URL-encoded game name

# Games list from the dataset
games_list = games_df['Title'].to_list()  # No need for the empty string here

# Safely find the index of the default game in the dataset, using a case-insensitive comparison
default_game_lower = default_game.lower().strip()
default_index = 0  # Default to "Select a game" option
for i, game in enumerate(games_list):
    if game.lower().strip() == default_game_lower:
        default_index = i
        break

# Selectbox to choose game
selected_game = ph.selectbox(
    'Select one among the 787 games from the menu: (you can type it as well)',
    ['Select a game'] + games_list,  # Add "Select a game" as the first option
    index=default_index + 1 if default_in
