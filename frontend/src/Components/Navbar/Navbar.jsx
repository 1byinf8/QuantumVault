import "./Navbar.css";
import { useNavigate } from "react-router-dom";

export default function Navbar() {
  const navigate = useNavigate();
    const handleLogout = () => {
      localStorage.removeItem("authToken");
      localStorage.removeItem("user");
      navigate("/");
  };
  return (
    <div className="nav-container">
      <h1>Qrypto Vault</h1>
      <div className="nav-links">
        <p>Home</p>
        <p>About</p>
        <p>Contact Us</p>
        <p onClick={handleLogout}>Log out</p>
      </div>
      
    </div>
  );
}
