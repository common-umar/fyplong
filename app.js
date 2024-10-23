// app.js
function submitGameTitle() {
    const gameTitle = document.getElementById("gameTitle").value;
    // Redirect to the Streamlit app with the new game title as a query parameter
    window.location.href = `/?game=${encodeURIComponent(gameTitle)}`;
}
