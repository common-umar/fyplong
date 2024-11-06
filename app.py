import streamlit as st
import pandas as pd
import textwrap
import random

# Get URL query parameters
query_params = st.experimental_get_query_params()
default_game = query_params.get('game', [''])[0]  # Default to an empty string if 'game' is not in query
mode = query_params.get('mode', ['light'])[0]  # Default to 'light' mode if 'mode' is not in query
default_genre = query_params.get('genre', [''])[0]  # Default to an empty string if 'genre' is not in query

# Custom CSS for light and dark mode
text_color = "#ffffff" if mode == 'dark' else "#000000"

# Apply CSS styling based on the mode
st.markdown(
    f"""
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Montserrat:ital,wght@0,100..900;1,100..900&display=swap" rel="stylesheet">
    
    <style>
        .stApp {{
            background-color: transparent !important;
            color: {text_color} !important;
            font-family: 'Montserrat', sans-serif;
        }}
        h1, h2, h3, h4, h5, h6 {{
            color: {text_color} !important;
        }}
        .stAppHeader,
        .stToolbarActionButton,
        ._terminalButton_rix23_138,
        ._profileContainer_1yi6l_53,
        ._container_1yi6l_1 {{
            display: none !important;
        }}
    </style>
    """,
    unsafe_allow_html=True
)

@st.cache_data(persist=True)
def getdata():
    games_df = pd.read_csv('Games_dataset.csv', index_col=0)
    similarity_df = pd.read_csv('sim_matrix.csv', index_col=0)
    return games_df, similarity_df

games_df, similarity_df = getdata()

# Standardize game titles to lowercase for comparison
games_df['lower_title'] = games_df['Title'].str.lower()

# Convert game title from URL to lowercase for comparison
default_game_lower = default_game.lower()

# Check if a genre is provided through the URL
selected_genre = default_genre.strip().lower() if default_genre else ''

# Recommendations based on game selection
if default_game:
    # Check if the game exists in the similarity matrix
    if default_game in similarity_df.columns:
        link = 'https://en.wikipedia.org' + games_df[games_df.Title.str.lower() == default_game_lower].Link.values[0]
        
        # DF query for game-based recommendations
        matches = similarity_df[default_game].sort_values()[1:6]
        matches = matches.index.tolist()
        matches = games_df.set_index('Title').loc[matches]
        matches.reset_index(inplace=True)
        
        st.markdown(f"# The recommended games for [{default_game}]({link}) are:")
        cols = ['Genre', 'Developer', 'Publisher', 'Released in: Japan', 'North America', 'Rest of countries']
        
        for idx, row in matches.iterrows():
            st.markdown(f'### {idx + 1} - {row["Title"]}')
            plot_text = row['Plots'] if pd.notna(row['Plots']) else "No plot information available."
            wrapped_plot = textwrap.wrap(plot_text, 600)[0]
            link_text = row['Link'] if pd.notna(row['Link']) else ""
            st.markdown(f'{wrapped_plot} [[...]](https://en.wikipedia.org{link_text})' if link_text else wrapped_plot)
            st.table(pd.DataFrame(row[cols]).T.set_index('Genre'))
            if link_text:
                st.markdown(f'Link to wiki page: [{row["Title"]}](https://en.wikipedia.org{link_text})')
    else:
        st.error(f"Game '{default_game}' not found in the recommendation database.")

# Genre-based recommendations
elif selected_genre:
    matched_games = games_df[games_df['Genre'].str.lower() == selected_genre]
    
    if not matched_games.empty:
        matched_games = matched_games.sample(n=min(5, len(matched_games)), random_state=random.randint(0, 100))
        st.markdown(f"# Recommended games for genre: **{selected_genre}**")
        
        for idx, row in matched_games.iterrows():
            st.markdown(f'### {idx + 1} - {row["Title"]}')
            plot_text = row['Plots'] if pd.notna(row['Plots']) else "No plot information available."
            wrapped_plot = textwrap.wrap(plot_text, 600)[0]
            link_text = row['Link'] if pd.notna(row['Link']) else ""
            st.markdown(f'{wrapped_plot} [[...]](https://en.wikipedia.org{link_text})' if link_text else wrapped_plot)
            st.table(pd.DataFrame(row[['Genre', 'Developer', 'Publisher', 'Released in: Japan', 'North America', 'Rest of countries']]).T.set_index('Genre'))
            if link_text:
                st.markdown(f'Link to wiki page: [{row["Title"]}](https://en.wikipedia.org{link_text})')
            else:
                st.markdown("No link available for this game.")
    else:
        st.error(f'No games found for the genre: {selected_genre}')

else:
    st.markdown('# Game recommendation :video_game:')
    st.text('')
    st.markdown('> _So you have a Nintendo Switch, just finished an amazing game, and would like to get recommendations for similar games?_')
    st.text('')
    st.markdown("This app lets you select a game from the dropdown menu and you'll get five recommendations that are the closest to your game according to the gameplay and/or plot.")
    st.text('')
    st.warning(':point_left: Enter a game or genre in the URL parameters for recommendations!')
