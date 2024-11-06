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
    <style>
        .stApp {{ background-color: transparent !important; color: {text_color} !important; font-family: 'Montserrat', sans-serif; }}
        h1, h2, h3, h4, h5, h6 {{ color: {text_color} !important; }}
        .stMarkdown, .stText, .stTitle, .stHeader, .stCaption, .stWidget, .stButton {{ color: {text_color} !important; }}
        .stAppHeader, .stToolbarActionButton, ._terminalButton_rix23_138, ._profileContainer_1yi6l_53, ._container_1yi6l_1 {{ display: none !important; }}
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

# Fetch game from URL query parameters
default_game_lower = default_game.lower()

# Check if a genre is provided through the URL
selected_genre = default_genre.strip().lower() if default_genre else ''


# Recommendations based on game selection
if default_game:
    if default_game_lower in games_df['lower_title'].values:
        # Retrieve the selected game’s data from games_df
        selected_game_data = games_df[games_df['lower_title'] == default_game_lower]
        selected_game_title = selected_game_data['Title'].values[0]
        
        # Check if the selected game exists in similarity_df
        if selected_game_title in similarity_df.columns:
            # Retrieve game recommendations
            link = 'https://en.wikipedia.org' + selected_game_data['Link'].values[0]
            matches = similarity_df[selected_game_title].sort_values()[1:6]
            matches = matches.index.tolist()
            matches = games_df.set_index('Title').loc[matches]
            matches.reset_index(inplace=True)

            st.markdown(f"# The recommended games for [{selected_game_title}]({link}) are:")
            # Display the selected game details in a table
            cols = ['Title', 'Genre', 'Developer', 'Publisher', 'Released in: Japan', 'North America', 'Rest of countries']
            st.markdown(f"### Game details for {selected_game_title}:")
            st.table(selected_game_data[cols].T)

            for idx, row in matches.iterrows():
                st.markdown(f'### {idx + 1} - {row["Title"]}')
                plot_text = row['Plots'] if pd.notna(row['Plots']) else "No plot information available."
                st.markdown('{} [[...]](https://en.wikipedia.org{})'.format(textwrap.wrap(plot_text, 600)[0], row['Link']))
                st.markdown(f'Link to wiki page: [{row["Title"]}](https://en.wikipedia.org{row["Link"]})')
        else:
            st.error(f"Game '{selected_game_title}' not found in the recommendation database.")
    else:
        st.error(f"Game '{default_game}' not found in the games database.")

# Genre-based recommendations
elif selected_genre:
    # Fetch games that match the selected genre
    matched_games = games_df[games_df['Genre'].str.lower() == selected_genre]
    
    if not matched_games.empty:
        # Randomly sample 5 games if there are more than 5 matches
        matched_games = matched_games.sample(n=min(5, len(matched_games)), random_state=random.randint(0, 100))
        
        st.markdown(f"# Recommended games for genre: **{selected_genre}**")
        
        for idx, row in matched_games.iterrows():
            st.markdown(f'### {idx + 1} - {row["Title"]}')
            plot_text = row['Plots'] if pd.notna(row['Plots']) else "No plot information available."
            link_text = row['Link'] if pd.notna(row['Link']) else ""
            wrapped_plot = textwrap.wrap(plot_text, 600)[0] if plot_text else "No plot information available."
            st.markdown(f'{wrapped_plot} [[...]](https://en.wikipedia.org{link_text})' if link_text else wrapped_plot)
            
            # Display game details in a table
            cols = ['Title', 'Genre', 'Developer', 'Publisher', 'Released in: Japan', 'North America', 'Rest of countries']
            st.table(row[cols].to_frame().T)
            
            # Link to Wikipedia page if available
            st.markdown(f'Link to wiki page: [{row["Title"]}](https://en.wikipedia.org{link_text})' if link_text else "No link available for this game.")
    else:
        st.error(f'No games found for the genre: {selected_genre}')




else:
    st.markdown('# Game recommendation :video_game:')
    st.markdown('> _So you have a Nintendo Switch, just finished an amazing game, and would like to get recommendations for similar games?_')
    st.warning(':point_left: Enter a game or genre in the URL parameters for recommendations!')
