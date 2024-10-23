import React, { useState } from 'react';
import { View, TextInput, Button } from 'react-native';

const GameInput = () => {
    const [gameTitle, setGameTitle] = useState('');

    const submitGameTitle = () => {
        // Redirect to the Streamlit app with the new game title as a query parameter
        const url = `http://localhost:8501/?game=${encodeURIComponent(gameTitle)}`;
        // Open the URL in the user's default web browser
        Linking.openURL(url).catch(err => console.error("Couldn't load page", err));
    };

    return (
        <View>
            <TextInput
                placeholder="Enter game title"
                value={gameTitle}
                onChangeText={setGameTitle}
            />
            <Button title="Get Recommendations" onPress={submitGameTitle} />
        </View>
    );
};

export default GameInput;
