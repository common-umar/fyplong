import streamlit as st
import pandas as pd
import textwrap


# Get URL query parameters
query_params = st.experimental_get_query_params()
default_game = query_params.get('game', [''])[0]  # Default to an empty string if 'game' is not in query
mode = query_params.get('mode', ['light'])[0]  # Default to 'light' mode if 'mode' is not in query

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

# Standardize game titles and genres to lowercase for comparison
games_df['lower_title'] = games_df['Title'].str.lower()
games_df['lower_genre'] = games_df['Genre'].str.lower()

# Fetch game or genre from URL query parameters
query_params = st.experimental_get_query_params()
default_game_or_genre = query_params.get('game', [''])[0].lower()  # Default to empty string if 'game' not in query

games_list = [''] + games_df['Title'].to_list()  # Include empty string for "Select a game" option
genres_list = games_df['Genre'].unique().tolist()

# Check if input matches a game title or genre
if default_game_or_genre in games_df['lower_title'].values:
    selected_type = 'game'
    default_index = games_df['lower_title'].tolist().index(default_game_or_genre) + 1  # +1 for empty string
elif default_game_or_genre in games_df['lower_genre'].values:
    selected_type = 'genre'
else:
    selected_type = None
    default_index = 0  # Default to first option ("Select a game")

# Selectbox for game selection
selected_game_or_genre = st.selectbox(
    'Select a game or enter a genre for recommendations:',
    games_list,
    index=default_index,
    key='default',
    format_func=lambda x: 'Select a game or genre' if x == '' else x
)

# Show recommendations based on game or genre
if selected_game_or_genre:
    if selected_type == 'game':
        # Get recommendations based on selected game
        link = 'https://en.wikipedia.org' + games_df[games_df.Title == selected_game_or_genre].Link.values[0]
        matches = similarity_df[selected_game_or_genre].sort_values()[1:6].index.tolist()
        matches = games_df.set_index('Title').loc[matches]
        matches.reset_index(inplace=True)
        recommendations = matches[['Title', 'Genre', 'Developer', 'Publisher', 'Plots', 'Link']].to_dict(orient='records')
        
        st.markdown("# Recommended games for [{}]({}) are:".format(selected_game_or_genre, link))
        
    elif selected_type == 'genre':
        # Get recommendations based on selected genre
        genre_matches = games_df[games_df['lower_genre'] == default_game_or_genre].sample(5)  # Random 5 games in genre
        recommendations = genre_matches[['Title', 'Genre', 'Developer', 'Publisher', 'Plots', 'Link']].to_dict(orient='records')
        
        st.markdown(f"# Recommended games in genre '{selected_game_or_genre.capitalize()}':")
    
    # Display recommendations
    for idx, game in enumerate(recommendations):
        st.markdown(f"### {idx + 1}. {game['Title']} - {game['Genre']}")
        st.markdown('{} [[...]](https://en.wikipedia.org{})'.format(textwrap.wrap(game['Plots'], 600)[0], game['Link']))
        cols = ['Genre', 'Developer', 'Publisher']
        st.table(pd.DataFrame([game]).T.loc[cols])
        st.markdown(f"Link to wiki page: [{game['Title']}]({game['Link']})")

else:
    # Default instructions if no game or genre is selected
    st.markdown('# Game Recommendation :video_game:')
    st.text('')
    st.markdown('> _Select a game or genre from the dropdown menu for personalized recommendations._')
    st.warning(':point_left: Select a game or enter a genre in the input box!')
