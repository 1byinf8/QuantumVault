// import './App.css';
// import Login from "./Pages/Login/Login"
// import Home from "./Pages/Home/Home"

// function App() {
//   return (
//     <div className="App">
//       <Login/>
//     </div>
//   );
// }

// export default App;

// /Users/1byinf8/Documents/QRYPTOVAULT/frontend/src/App.js
// /Users/1byinf8/Documents/QRYPTOVAULT/frontend/src/App.js
import React from 'react';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import './App.css';
import Login from './Pages/Login/Login';
import Home from './Pages/Home/Home';

  export default function App() {
    return (
      <Router>
        <Routes>
          <Route path="/" element={<Login />} />
          <Route path="/home" element={<Home />} />
        </Routes>
      </Router>
    );
  }
