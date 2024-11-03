import streamlit as st
import pandas as pd

# Load the CSV file
games_df = pd.read_csv('games.csv')

# Preprocess data: create a lowercase title for matching
games_df['lower_title'] = games_df['Title'].str.lower()

# Streamlit app layout
st.title("Game Recommendation System")
mode = st.sidebar.selectbox("Select mode", ["light", "dark"])

# Set the background color based on the mode
if mode == "dark":
    st.markdown(
        """
        <style>
        body {
            background-color: #1e1e1e;
            color: white;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
else:
    st.markdown(
        """
        <style>
        body {
            background-color: white;
            color: black;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

# User input for game title or genre
input_text = st.text_input("Enter a game name or genre:")

if input_text:
    # Check if input is a genre or a game title
    if input_text.lower() in games_df['Genre'].str.lower().values:
        # If input is a genre, get games of that genre
        recommended_games = games_df[games_df['Genre'].str.lower() == input_text.lower()]
    elif input_text.lower() in games_df['lower_title'].values:
        # If input is a game title, get the specific game
        selected_game = games_df[games_df['lower_title'] == input_text.lower()]
        link = 'https://en.wikipedia.org' + selected_game['Link'].values[0]
        genre = selected_game['Genre'].values[0]

        # Get 5 recommended games of the same genre
        recommended_games = games_df[games_df['Genre'] == genre].sample(n=5)
        
        # Display selected game and link
        st.write(f"### Recommended Game: {selected_game['Title'].values[0]}")
        st.write(f"[Link to Wikipedia]({link})")
    else:
        # If neither, return an error message
        st.write("No matching game or genre found. Please try again.")
        recommended_games = pd.DataFrame()  # Empty DataFrame for no recommendations

    # Display recommended games if available
    if not recommended_games.empty:
        st.write("### Recommended Games:")
        for index, row in recommended_games.iterrows():
            st.write(f"- **{row['Title']}** (Genre: {row['Genre']})")
