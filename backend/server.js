// server.js
const express = require('express');
const cors = require('cors');
const querystring = require('querystring');
require('dotenv').config();

const app = express();
const PORT = process.env.PORT || 3000;

// Middleware
app.use(cors({
    origin: "http://127.0.0.1:5173", // or http://localhost:5173
    methods: ["GET", "POST"],
    credentials: true
}));
app.use(express.json());

// Helper: generate random state string for Spotify auth
function generateRandomString(length) {
    let text = '';
    const possible = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
    for (let i = 0; i < length; i++) {
        text += possible.charAt(Math.floor(Math.random() * possible.length));
    }
    return text;
}

// Routes
app.get('/', (req, res) => {
    res.send('✅ Backend is running!');
});

app.get('/login', (req, res) => {
    const state = generateRandomString(16);
    const scope = 'user-read-private user-read-email';

    res.redirect('https://accounts.spotify.com/authorize?' +
        querystring.stringify({
            response_type: 'code',
            client_id: process.env.CLIENT_ID,
            scope: scope,
            redirect_uri: process.env.REDIRECT_URI,
            state: state
        }));

});

app.get('/callback', async (req, res) => {
    const code = req.query.code || null;

    if (!code) {
        return res.redirect('/#' + querystring.stringify({ error: 'no_code' }));
    }

    try {
        const params = new URLSearchParams();
        params.append("code", code);
        params.append("redirect_uri", process.env.REDIRECT_URI); // must match Spotify dashboard
        params.append("grant_type", "authorization_code");

        const response = await fetch("https://accounts.spotify.com/api/token", {
            method: "POST",
            headers: {
                "Authorization": "Basic " + Buffer.from(
                    process.env.CLIENT_ID + ":" + process.env.CLIENT_SECRET
                ).toString("base64"),
                "Content-Type": "application/x-www-form-urlencoded"
            },
            body: params
        });

        const data = await response.json();
        console.log("Spotify token response:", data);

        // ✅ Redirect to frontend with token in URL
        res.redirect(`http://127.0.0.1:5173/?access_token=${data.access_token}`);
        // res.json(data);
    } catch (err) {
        console.error("Error exchanging code:", err);
        res.status(500).send("Error getting token");
    }
});



// Start server
app.listen(PORT, () => {
    console.log(`✅ Server started and running at http://localhost:${PORT}`);
});

// Catch unhandled errors so process doesn't exit silently
process.on('uncaughtException', (err) => {
    console.error('❌ Uncaught Exception:', err);
});
process.on('unhandledRejection', (reason, promise) => {
    console.error('❌ Unhandled Rejection:', reason);
});
