document.getElementById('gameForm').addEventListener('submit', function(event) {
    event.preventDefault(); // Prevent the default form submission which reloads the page

    // Get the value from the input
    const gameTitle = document.getElementById('gameInput').value;

    // Redirect to the Streamlit app with the game title as a query parameter
    window.location.href = `/?game=${encodeURIComponent(gameTitle)}`; // Opens in the current tab
});
