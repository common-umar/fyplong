import streamlit as st
import pandas as pd
import textwrap

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

games_list = [''] + games_df['Title'].to_list()  # Include empty string for "Select a game" option

# Find the index of the default game in the dataset
if default_game_lower in games_df['lower_title'].values:
    default_index = games_df['lower_title'].tolist().index(default_game_lower) + 1  # +1 for the empty string
else:
    default_index = 0  # Default to the first option ("Select a game")

# Selectbox to choose game
selected_game = st.selectbox(
    'Select one among the 787 games from the menu: (you can type it as well)',
    games_list,
    index=default_index,
    key='default',
    format_func=lambda x: 'Select a game' if x == '' else x
)

# Check if a genre is provided through the URL
if default_genre:
    selected_genre = default_genre.strip().lower()
else:
    selected_genre = ''  # If no genre provided, default to empty

# Recommendations based on game selection
if selected_game:
    link = 'https://en.wikipedia.org' + games_df[games_df.Title == selected_game].Link.values[0]

    # DF query for game-based recommendations
    matches = similarity_df[selected_game].sort_values()[1:6]
    matches = matches.index.tolist()
    matches = games_df.set_index('Title').loc[matches]
    matches.reset_index(inplace=True)

    # Prepare response data
    response_data = matches[['Title', 'Genre', 'Developer', 'Publisher', 'Plots', 'Link']].to_dict(orient='records')

    # Results for selected game
    cols = ['Genre', 'Developer', 'Publisher', 'Released in: Japan', 'North America', 'Rest of countries']

    st.markdown(f"# The recommended games for [{selected_game}]({link}) are:")
    for idx, row in matches.iterrows():
        st.markdown(f'### {idx + 1} - {row["Title"]}')
        st.markdown(
            '{} [[...]](https://en.wikipedia.org{})'.format(textwrap.wrap(row['Plots'][0:], 600)[0], row['Link']))
        st.table(pd.DataFrame(row[cols]).T.set_index('Genre'))
        st.markdown(f'Link to wiki page: [{row["Title"]}](https://en.wikipedia.org{row["Link"]})')

# Genre-based recommendations
elif selected_genre:
    # Fetching games that match the selected genre
    matched_games = games_df[games_df['Genre'].str.lower() == selected_genre]
    
    if not matched_games.empty:
        st.markdown(f"# Recommended games for genre: **{selected_genre}**")
        # Sample 5 random games from the matched ones
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
    st.warning(':point_left: Select a game from the dropdown menu or type a genre for recommendations!')
