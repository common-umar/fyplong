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
if mode == 'dark':
    text_color = "#ffffff"  # Light text for dark mode
else:  # Light mode as default
    text_color = "#000000"  # Dark text for light mode

# Apply CSS styling based on the mode
st.markdown(
    f"""
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Montserrat:ital,wght@0,100..900;1,100..900&display=swap" rel="stylesheet">
    
    <style>
        /* Transparent background and font styling based on mode */
        .stApp {{
            background-color: transparent !important;
            color: {text_color} !important;
            font-family: 'Montserrat', sans-serif;
        }}

        /* Header and button text color based on mode */
        h1, h2, h3, h4, h5, h6 {{
            font-family: 'Montserrat', sans-serif !important;
            color: {text_color} !important;
        }}

        /* Additional styling to apply text color to all main text elements */
        .stMarkdown, .stText, .stTitle, .stHeader, .stCaption, .stWidget, .stButton {{
            color: {text_color} !important;
        }}

        /* Hide specific header and buttons */
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

# Fetch game from URL query parameters
default_game_lower = default_game.lower()

# Check if a genre is provided through the URL
selected_genre = default_genre.strip().lower() if default_genre else ''  # If no genre provided, default to empty

# Recommendations based on game selection
if default_game:
    link = 'https://en.wikipedia.org' + games_df[games_df.Title.str.lower() == default_game_lower].Link.values[0]

    # DF query for game-based recommendations
    matches = similarity_df[default_game].sort_values()[1:6]
    matches = matches.index.tolist()
    matches = games_df.set_index('Title').loc[matches]
    matches.reset_index(inplace=True)

    # Prepare response data
    response_data = matches[['Title', 'Genre', 'Developer', 'Publisher', 'Plots', 'Link']].to_dict(orient='records')

    # Results for selected game
    cols = ['Genre', 'Developer', 'Publisher', 'Released in: Japan', 'North America', 'Rest of countries']

    st.markdown(f"# The recommended games for [{default_game}]({link}) are:")
    for idx, row in matches.iterrows():
        st.markdown(f'### {idx + 1} - {row["Title"]}')
        st.markdown(
            '{} [[...]](https://en.wikipedia.org{})'.format(textwrap.wrap(row['Plots'][0:], 600)[0], row['Link']))
        st.table(pd.DataFrame(row[cols]).T.set_index('Genre'))
        st.markdown(f'Link to wiki page: [{row["Title"]}](https://en.wikipedia.org{row["Link"]})')

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
            
            # Ensure 'Plots' and 'Link' are available
            plot_text = row['Plots'] if pd.notna(row['Plots']) else "No plot information available."
            link_text = row['Link'] if pd.notna(row['Link']) else ""
            
            # Wrap plot text if available
            wrapped_plot = textwrap.wrap(plot_text, 600)[0] if plot_text else "No plot information available."
            st.markdown(f'{wrapped_plot} [[...]](https://en.wikipedia.org{link_text})' if link_text else wrapped_plot)
            
            # Show additional details in a table
            st.table(pd.DataFrame(row[['Genre', 'Developer', 'Publisher', 'Released in: Japan', 'North America', 'Rest of countries']]).T.set_index('Genre'))
            
            # Link to Wikipedia page if available
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
