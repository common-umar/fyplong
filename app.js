document.getElementById('gameForm').addEventListener('submit', function(event) {
    event.preventDefault(); // Prevent default form submission

    // Get the value from the input
    const gameTitle = document.getElementById('gameInput').value;

    // Redirect to the Streamlit app with the game title as a query parameter
    window.location.href = `/?game=${encodeURIComponent(gameTitle)}`;
});
