import streamlit as st
import pandas as pd
import textwrap

st.header(
    """ 
    <style> 
    #MainMenu {visibility: hidden;} 
    footer {visibility: hidden;} 
    header {visibility: hidden;} 
    </style> 
    """
)
# Add custom CSS to hide the GitHub icon
hide_github_icon = """
#GithubIcon {
  visibility: hidden;
}
"""

st.markdown(hide_github_icon, unsafe_allow_html=True)
# Set background color to white (RGB)
st.markdown(
    """
    <style>
    body {
        background-color: rgb(255, 255, 255);
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Load and Cache the data
@st.cache_data(persist=True)
def getdata():
    games_df = pd.read_csv('Games_dataset.csv', index_col=0)
    similarity_df = pd.read_csv('sim_matrix.csv', index_col=0)
    return games_df, similarity_df

games_df, similarity_df = getdata()

# Standardize game titles to lowercase for comparison
games_df['lower_title'] = games_df['Title'].str.lower()

# Fetch game from URL query parameters
query_params = st.experimental_get_query_params()
default_game = query_params.get('game', [''])[0]  # Default to an empty string if 'game' is not in query

# Lowercase the default game for comparison
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

# Recommendations
if selected_game:
    link = 'https://en.wikipedia.org' + games_df[games_df.Title == selected_game].Link.values[0]

    # DF query
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

