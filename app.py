import streamlit as st
import pandas as pd
import textwrap

# Load and Cache the data
@st.cache_data(persist=True)
def getdata():
    games_df = pd.read_csv('Games_dataset.csv', index_col=0)
    similarity_df = pd.read_csv('sim_matrix.csv', index_col=0)
    return games_df, similarity_df

games_df, similarity_df = getdata()

# Set a hardcoded game title (you can change this to test different games)
DEFAULT_GAME_TITLE = "140"  # Change this to your desired game title

# Sidebar
st.sidebar.markdown('<strong><span style="color: #8B2500;font-size: 26px;"> Game recommendation</span></strong>', unsafe_allow_html=True)
st.sidebar.markdown('An app by [Long Do](https://doophilong.github.io/Portfolio/)')
st.sidebar.image('pexels-pixabay-275033.jpg', use_column_width=True)
st.sidebar.markdown('<strong><span style="color: #EE4000;font-size: 26px;">:slot_machine: Choose your game !!!</span></strong>', unsafe_allow_html=True)

# Get query parameters for game title
query_params = st.experimental_get_query_params()
if 'game' in query_params:
    selected_game = query_params['game'][0]
else:
    selected_game = DEFAULT_GAME_TITLE  # Use the hardcoded title as default

# Update session state for selected game
if 'selected_game' not in st.session_state:
    st.session_state.selected_game = selected_game

# Text input for game title
game_title_input = st.text_input("Enter a game title:", value=st.session_state.selected_game)

# Button to submit the title
if st.button("Get Recommendations"):
    st.session_state.selected_game = game_title_input  # Update the session state

# Generate game list
games_list = [''] + games_df['Title'].to_list()  # Include empty string for "Select a game" option
default_index = 0 if st.session_state.selected_game not in games_list else games_list.index(st.session_state.selected_game)

selected_game = st.selectbox(
    'Select one among the 787 games from the menu: (you can type it as well)',
    games_list, 
    index=default_index,
    key='default',
    format_func=lambda x: 'Select a game' if x == '' else x
)

# Update session state when a game is selected
if selected_game:
    st.session_state.selected_game = selected_game

# Recommendations
if st.session_state.selected_game:
    link = 'https://en.wikipedia.org' + games_df[games_df.Title == st.session_state.selected_game].Link.values[0]

    # DF query
    matches = similarity_df[st.session_state.selected_game].sort_values()[1:6]
    matches = matches.index.tolist()
    matches = games_df.set_index('Title').loc[matches]
    matches.reset_index(inplace=True)
    
    # Prepare response data
    response_data = matches[['Title', 'Genre', 'Developer', 'Publisher', 'Plots', 'Link']].to_dict(orient='records')
    
    # Return JSON response
    st.json(response_data)  # This will display JSON in the Streamlit app

    # Results
    cols = ['Genre', 'Developer', 'Publisher', 'Released in: Japan', 'North America', 'Rest of countries']
    
    st.markdown("# The recommended games for [{}]({}) are:".format(st.session_state.selected_game, link))
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
