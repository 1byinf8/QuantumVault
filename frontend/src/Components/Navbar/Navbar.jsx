import "./Navbar.css";

export default function Navbar() {
    const handleLogout = () => {
      localStorage.removeItem("authToken");
      localStorage.removeItem("user");
      window.location.href = "/login";
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
