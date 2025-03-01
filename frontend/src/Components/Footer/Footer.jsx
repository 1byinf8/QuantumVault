import "./Footer.css";

export default function Footer() {
  return (
    <div className="footer-container">
        <p className="header"><span>Qrypto Vault</span> : Secure Your Digital Assets with Quantum-Secure Blockchain</p>
        <div className="footer-links">
          <a href="#">Privacy Policy</a>
          <a href="#">Terms of Service</a>
          <a href="#">FAQ</a>
          <a href="#">Support</a>
        </div>
        <p className="copyright">
          &copy; {new Date().getFullYear()} Qrypto Vault. All rights reserved.
        </p>
    </div>
  );
}
