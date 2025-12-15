import React, { useState, useEffect } from "react";
import {
  BrowserRouter as Router,
  Routes,
  Route,
  Link,
  Navigate
} from "react-router-dom";

import Detection from "./pages/Detection";
import Login from "./pages/Login";
import Signup from "./pages/Signup";
import Logout from "./pages/Logout";
import "./App.css";

function App() {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [authChecked, setAuthChecked] = useState(false); // 🔥 NEW

  // Check login status on page load
  useEffect(() => {
    const user = localStorage.getItem("user");
    setIsLoggedIn(!!user);
    setAuthChecked(true); // 🔥 auth resolved
  }, []);

  // 🔥 Prevent rendering until auth check is done
  if (!authChecked) {
    return null; // or loading spinner
  }

  return (
    <Router>
      <div className="app-container">
        <header className="header">
          <nav>
            <h1>GlaucoAI</h1>
            <ul>
              {/* Show Detection ONLY after login */}
              {isLoggedIn && (
                <li>
                  <Link to="/">Detection</Link>
                </li>
              )}

              {!isLoggedIn ? (
                <>
                  <li>
                    <Link to="/login">Login</Link>
                  </li>
                  <li>
                    <Link to="/signup">Signup</Link>
                  </li>
                </>
              ) : (
                <li>
                  <Link to="/logout">Logout</Link>
                </li>
              )}
            </ul>
          </nav>
        </header>

        <Routes>
          {/* Protected Detection route */}
          <Route
            path="/"
            element={
              isLoggedIn ? <Detection /> : <Navigate to="/login" replace />
            }
          />

          <Route
            path="/login"
            element={<Login setIsLoggedIn={setIsLoggedIn} />}
          />
          <Route path="/signup" element={<Signup />} />
          <Route
            path="/logout"
            element={<Logout setIsLoggedIn={setIsLoggedIn} />}
          />
        </Routes>
      </div>
    </Router>
  );
}

export default App;
