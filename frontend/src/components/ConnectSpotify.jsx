import { useState } from "react";
import { useEffect } from "react";

const ConnectSpotify = () => {
  const [loggedin, setLoggedIn] = useState(false);
  // const [token, setToken] = useState(null);
  const [songs, setSongs] = useState([]);

  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const accessToken = params.get("access_token");
    if (accessToken) {
      // setToken(accessToken);
      setLoggedIn(true);
      window.history.replaceState({}, document.title, "/");
      fetchLikedSongs(accessToken);
    }
  }, []);

  function login() {
    // just redirect to backend /login
    window.location.href = "http://localhost:3000/login";
  }

  async function fetchLikedSongs(token) {
    try {
      const res = await fetch("http://localhost:3000/get-liked-songs", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ accessToken: token })
      })

      const data = await res.json();
      setSongs(data);
      // console.log('songs data:', data);

    } catch (error) {
      console.log(error)
    }

  }

  return (
    <div>
      {loggedin ? (
        <div>
          <h2>Your Liked Songs:</h2>
          {songs.length > 0 ? (
            songs.map((song, i) => (
              <p key={i}>
                {song.name} — {song.artist}
              </p>
            ))
          ) : (
            <p>Loading songs...</p>
          )}
        </div>
      ) : (
        <button onClick={login}>Login with Spotify</button>
      )}
    </div>
  );
};

export default ConnectSpotify;