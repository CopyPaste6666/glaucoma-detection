import React, { useState, useEffect } from "react";
import { BrowserRouter as Router, Routes, Route, Link, Navigate } from "react-router-dom";
import Detection from "./pages/Detection";
import Login from "./pages/Login";
import Signup from "./pages/Signup";
import Logout from "./pages/Logout";
import "./App.css";

function App() {
  const [isLoggedIn, setIsLoggedIn] = useState(false);

  // Check login status on page load
  useEffect(() => {
    const user = localStorage.getItem("user");
    if (user) {
      setIsLoggedIn(true);
    }
  }, []);

  return (
    <Router>
      <div className="app-container">
        <header className="header">
          <nav>
            <h1>GlaucoAI</h1>
            <ul>
              {/* Only show Detection when logged in */}
              {isLoggedIn && <li><Link to="/">Detection</Link></li>}

              {!isLoggedIn ? (
                <>
                  <li><Link to="/login">Login</Link></li>
                  <li><Link to="/signup">Signup</Link></li>
                </>
              ) : (
                <li><Link to="/logout">Logout</Link></li>
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

          <Route path="/login" element={<Login setIsLoggedIn={setIsLoggedIn} />} />
          <Route path="/signup" element={<Signup />} />
          <Route path="/logout" element={<Logout setIsLoggedIn={setIsLoggedIn} />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;
