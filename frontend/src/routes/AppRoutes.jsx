/**
 * Frontend route map.
 *
 * Keep route definitions centralized here.
 */
import { Routes, Route } from "react-router-dom";
import Home from "../pages/Home";
import PlaceDetail from "../pages/PlaceDetail";
import MapView from "../pages/MapView";
import RouteView from "../pages/RouteView";
import Favorites from "../pages/Favorites";
import SocialFeed from "../pages/SocialFeed";
import Login from "../pages/Login";
import Register from "../pages/Register";
import Profile from "../pages/Profile";
import Admin from "../pages/Admin";

export default function AppRoutes() {
  return (
    <Routes>
      <Route path="/" element={<Home />} />
      <Route path="/places/:id" element={<PlaceDetail />} />
      <Route path="/map" element={<MapView />} />
      <Route path="/route" element={<RouteView />} />
      <Route path="/favorites" element={<Favorites />} />
      <Route path="/social" element={<SocialFeed />} />
      <Route path="/login" element={<Login />} />
      <Route path="/register" element={<Register />} />
      <Route path="/profile" element={<Profile />} />
      <Route path="/admin" element={<Admin />} />
    </Routes>
  );
}
