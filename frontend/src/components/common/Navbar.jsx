import { Link } from "react-router-dom";

export default function Navbar() {
  return (
    <header className="navbar">
      <div className="container row" style={{ padding: 0, justifyContent: "space-between" }}>
        <strong>Travel Recommendation App</strong>
        <nav className="row">
          <Link to="/">Home</Link>
          <Link to="/map">Map</Link>
          <Link to="/route">Route</Link>
          <Link to="/favorites">Favorites</Link>
          <Link to="/login">Login</Link>
        </nav>
      </div>
    </header>
  );
}
