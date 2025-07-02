import React from "react";
import nebraska from "../assets/nebraska.png";
import '../App.css'
export const Header = () => {
  return (
    <div className="header">
      <div>
        <img src={nebraska} alt="Nebraska" height={80} width={80} />
      </div>
      <div className="button-container">
        <button className="button-header">Log In</button>
        <button className="button-header">Sign In</button>
      </div>
    </div>
  );
};