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

# Add a column for lowercase genre for comparison
games_df['lower_title'] = games_df['Title'].str.lower()
games_df['lower_genre'] = games_df['Genre'].str.lower()

# Fetch game or genre from URL query parameters
query_params = st.experimental_get_query_params()
input_value = query_params.get('game', [''])[0].lower()  # Convert input to lowercase

# Check if the input is a genre or a game title
is_genre = input_value in games_df['lower_genre'].values
is_game = input_value in games_df['lower_title'].values

# If the input is a genre, recommend 5 games in that genre
if is_genre:
    selected_genre = input_value.capitalize()
    genre_matches = games_df[games_df['lower_genre'] == input_value].head(5)  # Select the first 5 matches

    st.markdown(f"# Recommended games in the {selected_genre} genre:")
    for idx, row in genre_matches.iterrows():
        st.markdown(f'### {row["Title"]}')
        st.markdown(f'{textwrap.wrap(row["Plots"], 600)[0]} [[Read more]](https://en.wikipedia.org{row["Link"]})')
        
# If the input is a game title, proceed with the current recommendation logic
elif is_game:
    selected_game = input_value.capitalize()
    link = 'https://en.wikipedia.org' + games_df[games_df.lower_title == selected_game].Link.values[0]
    
    # DF query for similar games
    matches = similarity_df[selected_game].sort_values()[1:6]
    matches = matches.index.tolist()
    matches = games_df.set_index('Title').loc[matches]
    matches.reset_index(inplace=True)

    # Display recommended games
    st.markdown(f"# The recommended games for [{selected_game}]({link}) are:")
    for idx, row in matches.iterrows():
        st.markdown(f'### {row["Title"]}')
        st.markdown(f'{textwrap.wrap(row["Plots"], 600)[0]} [[Read more]](https://en.wikipedia.org{row["Link"]})')

# If input is neither a genre nor a game title, display the default message
else:
    st.markdown('# Game recommendation :video_game:')
    st.markdown('> _Select a game or genre from the dropdown menu or URL to get recommendations!_')
