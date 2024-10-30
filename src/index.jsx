import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App'; // Import your main App component
import './index.scss'; // Import your styles if necessary

// Render the App component in the root div
console.log("index will be mounted")
const root = ReactDOM.createRoot(document.getElementById("root"))
root.render(<App />);
