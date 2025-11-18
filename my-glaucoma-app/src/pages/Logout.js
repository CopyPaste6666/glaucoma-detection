import React, { useEffect } from "react";
import { useNavigate } from "react-router-dom";

function Logout({ setIsLoggedIn }) {
  const navigate = useNavigate();

  useEffect(() => {
    localStorage.removeItem("user");
    setIsLoggedIn(false);
    navigate("/login");
  }, [navigate, setIsLoggedIn]);

  return null;
}

export default Logout;
