/**
 * Frontend route map.
 *
 * Keep route definitions centralized here.
 */
import { Routes, Route } from "react-router-dom";
import Home from "../pages/Home";
import PlaceDetail from "../pages/PlaceDetail";
import MapView from "../pages/MapView";
import ReviewPage from "../pages/ReviewPage";
import RouteView from "../pages/RouteView";
import Favorites from "../pages/Favorites";
import Login from "../pages/Login";
import Register from "../pages/Register";

export default function AppRoutes() {
  return (
    <Routes>
      <Route path="/" element={<Home />} />
      <Route path="/places/:id" element={<PlaceDetail />} />
      <Route path="/map" element={<MapView />} />
      <Route path="/reviews" element={<ReviewPage />} />
      <Route path="/reviews/:placeId" element={<ReviewPage />} />
      <Route path="/route" element={<RouteView />} />
      <Route path="/favorites" element={<Favorites />} />
      <Route path="/login" element={<Login />} />
      <Route path="/register" element={<Register />} />
    </Routes>
  );
}
