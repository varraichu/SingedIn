import { useEffect } from "react";

const App = () => {
  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const token = params.get("access_token");
    if (token) {
      console.log("Spotify Access Token:", token);
      // you can save it in state or localStorage
      window.history.replaceState({}, document.title, "/");
    }
  }, []);

  function login() {
    // just redirect to backend /login
    window.location.href = "http://localhost:3000/login";
  }

  return (
    <div>
      <button onClick={login}>Login with Spotify</button>
    </div>
  );
};

export default App;
