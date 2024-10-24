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
    index=default_index + 1 if default_index > 0 else 0,  # Adjust index for 'Select a game'
    key='default'
)

# Recommendations
if selected_game != 'Select a game':  # Check that a game is selected
    link = 'https://en.wikipedia.org' + games_df[games_df.Title == selected_game].Link.values[0]

    # DF query for recommendations
    matches = similarity_df[selected_game].sort_values()[1:6]
    matches = matches.index.tolist()
    matches = games_df.set_index('Title').loc[matches]
    matches.reset_index(inplace=True)
    
    # Prepare response data
    response_data = matches[['Title', 'Genre', 'Developer', 'Publisher', 'Plots', 'Link']].to_dict(orient='records')
    
    # Return JSON response
    st.json(response_data)  # This will display JSON in the Streamlit app

    # Results
    cols = ['Genre', 'Developer', 'Publisher', 'Released in: Japan', 'North America', 'Rest of countries']
    
    st.markdown("# The recommended games for [{}]({}) are:".format(selected_game, link))
    for idx, row in matches.iterrows():
        st.markdown('### {} - {}'.format(str(idx + 1), row['Title']))
        st.markdown(
            '{} [[...]](https://en.wikipedia.org{})'.format(textwrap.wrap(row['Plots'][0:], 600)[0], row['Link']))
        st.table(pd.DataFrame(row[cols]).T.set_index('Genre'))
        st.markdown('Link to wiki page: [{}](https://en.wikipedia.org{})'.format(row['Title'], row['Link']))

else:
    st.markdown('# Game recommendation :video_game:')
    st.text('')
    st.markdown('> _So you have a Nintendo Switch, just finished an amazing game, and would like to get recommendations for similar games?_')
    st.text('')
    st.markdown("This app lets you select a game from the dropdown menu and you'll get five recommendations that are the closest to your game according to the gameplay and/or plot.")
    st.text('')
    st.warning(':point_left: Select a game from the dropdown menu!')
