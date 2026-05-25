import { useEffect, useMemo, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { CircleMarker, Tooltip } from "react-leaflet";
import { CheckCircle } from "lucide-react";

import MapContainer from "../components/map/MapContainer";
import MarkerList from "../components/map/MarkerList";
import RouteMap from "../components/map/RouteMap";
import Section from "../components/common/Section";
import { useAuth } from "../hooks/useAuth";
import { useApp } from "../hooks/useApp";
import {
  getCurrentBrowserLocation,
} from "../utils/geolocation";
import { addFavorite } from "../services/favoriteService";
import { recordPlacePick, resolvePlaceFromCoordinates } from "../services/mapPickService";
import { getRoute } from "../services/routeService";
import { recordVisitedPlace } from "../services/socialService";

const TRAVEL_MODES = [
  { value: "DRIVING", label: "Driving" },
  { value: "WALKING", label: "Walking" },
  { value: "BICYCLING", label: "Bicycling" },
  { value: "TRANSIT", label: "Transit" },
];

function buildPointMarker(color) {
  return {
    radius: 9,
    pathOptions: {
      color: "#ffffff",
      weight: 2,
      fillColor: color,
      fillOpacity: 1,
    },
  };
}

function buildTemporaryMapPlace(point, address = null) {
  const fallbackAddress = address || formatCoordinatePoint(point);
  return {
    id: `temp-route-${point.latitude}-${point.longitude}-${Date.now()}`,
    name: "Pinned point",
    address: fallbackAddress,
    latitude: point.latitude,
    longitude: point.longitude,
    photo_url: null,
    rating: null,
    review_count: 0,
    distance_km: null,
    _isTemporaryMapSelection: true,
    _isLocalOnly: true,
    _canView: false,
    _canSave: false,
  };
}

function coordinatePointToRequest(point) {
  return `${point.latitude},${point.longitude}`;
}

function formatCoordinatePoint(point) {
  return `${point.latitude.toFixed(5)}, ${point.longitude.toFixed(5)}`;
}

function coordinatePointFromPlace(place) {
  if (
    place &&
    typeof place.latitude === "number" &&
    typeof place.longitude === "number"
  ) {
    return {
      latitude: place.latitude,
      longitude: place.longitude,
    };
  }

  return null;
}

function sanitizePickedPlace(place) {
  if (!place) {
    return place;
  }

  const {
    _isTemporaryMapSelection,
    _isLocalOnly,
    _canView,
    _canSave,
    ...cleanPlace
  } = place;
  return cleanPlace;
}

export default function RouteView() {
  const navigate = useNavigate();
  const { isAuthenticated, hasCompletedProfile } = useAuth();
  const {
    selectedPlace,
    setSelectedPlace,
    currentLocation,
    setCurrentLocation,
    recommendationPlaces,
    setRecommendationPlaces,
  } = useApp();
  const [travelMode, setTravelMode] = useState("DRIVING");
  const [originMode, setOriginMode] = useState(currentLocation ? "gps" : "manual");
  const [selectionTarget, setSelectionTarget] = useState(
    currentLocation ? "destination" : "origin"
  );
  const [originInput, setOriginInput] = useState("");
  const [destinationInput, setDestinationInput] = useState("");
  const [originPoint, setOriginPoint] = useState(null);
  const [destinationPoint, setDestinationPoint] = useState(null);
  const [routeInfo, setRouteInfo] = useState(null);
  const [routeError, setRouteError] = useState("");
  const [loadingRoute, setLoadingRoute] = useState(false);
  const [savingVisitedPlace, setSavingVisitedPlace] = useState(false);
  const [routeCompletionMessage, setRouteCompletionMessage] = useState("");
  const [routeCompletionError, setRouteCompletionError] = useState("");
  const [locationNotice, setLocationNotice] = useState("");
  const [selectedPopupPlaceId, setSelectedPopupPlaceId] = useState(null);

  useEffect(() => {
    if (selectedPlace?.address) {
      setDestinationInput(selectedPlace.address);
    }

    if (
      selectedPlace &&
      typeof selectedPlace.latitude === "number" &&
      typeof selectedPlace.longitude === "number"
    ) {
      setDestinationPoint({
        latitude: selectedPlace.latitude,
        longitude: selectedPlace.longitude,
      });
    }
  }, [selectedPlace]);

  useEffect(() => {
    setRouteInfo(null);
    setRouteError("");
    setRouteCompletionMessage("");
    setRouteCompletionError("");
  }, [
    currentLocation,
    destinationInput,
    destinationPoint,
    originInput,
    originMode,
    originPoint,
    travelMode,
  ]);

  useEffect(() => {
    let active = true;

    async function hydrateLocation() {
      if (currentLocation) {
        setOriginMode("gps");
        setSelectionTarget("destination");
        return;
      }

      try {
        const browserLocation = await getCurrentBrowserLocation();
        if (!active) return;
        setCurrentLocation(browserLocation);
        setOriginMode("gps");
        setSelectionTarget("destination");
        setLocationNotice("Using your current GPS location as the default start point.");
      } catch (error) {
        if (!active) return;
        setOriginMode("manual");
        setSelectionTarget("origin");
        setLocationNotice("GPS is unavailable. Pick the start point on the map or enter it manually.");
      }
    }

    hydrateLocation();
    return () => {
      active = false;
    };
  }, [currentLocation, setCurrentLocation]);

  const canUseRoute = isAuthenticated && hasCompletedProfile;

  const mapCenter = useMemo(() => {
    if (selectionTarget === "destination" && destinationPoint) {
      return destinationPoint;
    }

    if (originMode === "gps" && currentLocation) {
      return currentLocation;
    }

    if (originPoint) {
      return originPoint;
    }

    if (destinationPoint) {
      return destinationPoint;
    }

    if (
      selectedPlace &&
      typeof selectedPlace.latitude === "number" &&
      typeof selectedPlace.longitude === "number"
    ) {
      return { latitude: selectedPlace.latitude, longitude: selectedPlace.longitude };
    }

    return { latitude: 10.7769, longitude: 106.7009 };
  }, [currentLocation, destinationPoint, originMode, originPoint, selectedPlace, selectionTarget]);

  const originForRequest =
    originMode === "gps" && currentLocation
      ? coordinatePointToRequest(currentLocation)
      : originPoint
      ? coordinatePointToRequest(originPoint)
      : originInput.trim();

  const destinationForRequest = destinationPoint
    ? coordinatePointToRequest(destinationPoint)
    : destinationInput.trim();

  const startSummary =
    originMode === "gps" && currentLocation
      ? formatCoordinatePoint(currentLocation)
      : originPoint
      ? formatCoordinatePoint(originPoint)
      : originInput || "Pick a point on the map or type it manually";

  const destinationSummary = destinationPoint
    ? formatCoordinatePoint(destinationPoint)
    : destinationInput || selectedPlace?.name || "Pick a place or click a destination on the map";

  const routeFitBoundsPoints = useMemo(
    () =>
      [
        ...(recommendationPlaces || []),
        originMode === "gps" ? currentLocation : originPoint,
        destinationPoint,
        ...(routeInfo?.path || []),
      ].filter(Boolean),
    [currentLocation, destinationPoint, originMode, originPoint, recommendationPlaces, routeInfo]
  );

  if (!canUseRoute) {
    return (
      <div className="card" style={{ display: "grid", gap: "12px", marginTop: "24px" }}>
        <h1>Profile required for Route</h1>
        <p style={{ marginBottom: 0 }}>
          You need a completed account profile before using route planning.
        </p>
        <p style={{ marginBottom: 0 }}>
          {isAuthenticated ? (
            <Link to="/profile" style={{ color: "var(--color-primary)", fontWeight: 700 }}>
              Complete profile
            </Link>
          ) : (
            <Link to="/login" style={{ color: "var(--color-primary)", fontWeight: 700 }}>
              Sign in to continue
            </Link>
          )}
        </p>
      </div>
    );
  }

  async function applyMapPoint(point, target) {
    setRouteError("");
    try {
      const resolvedPlace = await resolvePlaceFromCoordinates({
        latitude: point.latitude,
        longitude: point.longitude,
      });
      const alreadyListed = recommendationPlaces.some((place) => place.id === resolvedPlace.id);
      const previewPlace = {
        ...resolvedPlace,
        _isTemporaryMapSelection: !alreadyListed,
      };
      const mergedPlaces = [
        previewPlace,
        ...recommendationPlaces.filter((place) => place.id !== resolvedPlace.id),
      ];
      setRecommendationPlaces(mergedPlaces);
      setSelectedPopupPlaceId(previewPlace.id);
      setLocationNotice(
        target === "origin"
          ? "Map point previewed. Use Pick on map to confirm it as the start point."
          : "Map point previewed. Use Pick on map to confirm it as the destination."
      );
      return;
    } catch (error) {
      const fallbackPlace = buildTemporaryMapPlace(point);
      setRecommendationPlaces((previousPlaces) => [
        fallbackPlace,
        ...previousPlaces.filter((place) => place.id !== fallbackPlace.id),
      ]);
      setSelectedPopupPlaceId(fallbackPlace.id);
      setLocationNotice(
        target === "origin"
          ? "Map point previewed manually. Use Pick on map to confirm it as the start point."
          : "Map point previewed manually. Use Pick on map to confirm it as the destination."
      );
    }
  }

  async function handleMapClick(point) {
    await applyMapPoint(point, selectionTarget);
  }

  function removeTemporaryPreview(place) {
    if (!place?._isTemporaryMapSelection) {
      return;
    }

    setRecommendationPlaces((previousPlaces) =>
      previousPlaces.filter((item) => item.id !== place.id)
    );
  }

  function clearPreviewSelection(place) {
    setSelectedPopupPlaceId(null);
    if (place?._isTemporaryMapSelection) {
      removeTemporaryPreview(place);
    }
  }

  async function handleConfirmMapSelection(place) {
    setSelectedPopupPlaceId(place.id);
    const resolvedPoint = coordinatePointFromPlace(place);

    if (selectionTarget === "origin") {
      setOriginMode("manual");
      setOriginPoint(resolvedPoint);
      setOriginInput(
        place.address ||
          place.name ||
          (resolvedPoint ? coordinatePointToRequest(resolvedPoint) : "")
      );
      setLocationNotice("Start point confirmed from the map.");
      clearPreviewSelection(place);
      return;
    }

    if (typeof place.id === "number") {
      recordPlacePick(place.id).catch((error) => {
        console.error("Failed to record place pick", error);
      });
    }

    setSelectedPlace(place._isLocalOnly ? null : sanitizePickedPlace(place));
    setDestinationPoint(resolvedPoint);
    setDestinationInput(
      place.address ||
        place.name ||
        (resolvedPoint ? coordinatePointToRequest(resolvedPoint) : "")
    );
    setLocationNotice("Destination confirmed from the map.");
    clearPreviewSelection(place);
  }

  async function handleSavePlace(place) {
    if (place._canSave === false) {
      return;
    }

    try {
      await addFavorite(place.id);
      setLocationNotice("Place saved to your Saved list.");
      if (place._isTemporaryMapSelection) {
        setRecommendationPlaces((previousPlaces) =>
          previousPlaces.map((item) =>
            item.id === place.id
              ? {
                  ...item,
                  _isTemporaryMapSelection: false,
                }
              : item
          )
        );
      }
    } catch (error) {
      console.error("Failed to save place", error);
    }
  }

  async function handleRouteSubmit(event) {
    event.preventDefault();
    setRouteError("");

    if (!originForRequest || !destinationForRequest) {
      setRouteError("Please choose both a starting point and a destination.");
      setRouteInfo(null);
      return;
    }

    try {
      setLoadingRoute(true);
      const data = await getRoute({
        origin: originForRequest,
        destination: destinationForRequest,
        travel_mode: travelMode.toLowerCase(),
      });

      setRouteInfo({
        origin: data.origin,
        destination: data.destination,
        distance: data.distance_text,
        duration: data.duration_text,
        distanceKm: data.distance_km,
        durationSeconds: data.duration_seconds,
        path: data.path || [],
        steps: (data.steps || []).map((step) => ({
          instructions: step.instruction,
          distance: step.distance_text,
          duration: step.duration_text,
        })),
      });
    } catch (error) {
      setRouteInfo(null);
      setRouteError(
        error?.response?.data?.detail || "We couldn't calculate the route right now."
      );
    } finally {
      setLoadingRoute(false);
    }
  }

  async function handleCompleteRoute() {
    if (!routeInfo || typeof selectedPlace?.id !== "number") {
      setRouteCompletionError("Choose a catalog place as destination before marking this route complete.");
      return;
    }

    try {
      setSavingVisitedPlace(true);
      setRouteCompletionError("");
      const visitedPlace = await recordVisitedPlace({
        place_id: selectedPlace.id,
        route_origin: routeInfo.origin,
        route_destination: routeInfo.destination,
        distance_text: routeInfo.distance,
        duration_text: routeInfo.duration,
        distance_km: routeInfo.distanceKm,
        duration_seconds: routeInfo.durationSeconds,
        travel_mode: travelMode.toLowerCase(),
      });
      setRouteCompletionMessage(
        `${visitedPlace.place_name} has been added to your visited places.`
      );
    } catch (error) {
      setRouteCompletionError(
        error?.response?.data?.detail ||
          "We couldn't mark this route as completed right now."
      );
    } finally {
      setSavingVisitedPlace(false);
    }
  }

  async function handleUseGps() {
    try {
      const browserLocation = await getCurrentBrowserLocation();
      setCurrentLocation(browserLocation);
      setOriginMode("gps");
      setOriginPoint(null);
      setOriginInput("");
      setSelectionTarget("destination");
      setRouteError("");
      setLocationNotice("GPS location updated successfully.");
    } catch (error) {
      setOriginMode("manual");
      setSelectionTarget("origin");
      setLocationNotice("Unable to read GPS. Choose the starting point manually or by clicking the map.");
    }
  }

  const gpsMarkerIcon = buildPointMarker("#2563eb");
  const originMarkerIcon = buildPointMarker("#16a34a");
  const destinationMarkerIcon = buildPointMarker("#7c3aed");
  const canCompleteRoute = routeInfo && typeof selectedPlace?.id === "number";

  return (
    <div style={{ display: "grid", gap: "24px" }}>
      <Section
        title="Route Planner"
      >
        <form className="card" onSubmit={handleRouteSubmit} style={{ display: "grid", gap: "18px" }}>
          <div style={{ display: "grid", gap: "12px" }}>
            <strong style={{ color: "var(--color-text)" }}>Start point</strong>
            <div style={{ display: "flex", gap: "10px", flexWrap: "wrap" }}>
              <button
                type="button"
                className={originMode === "gps" ? "btn-primary" : "btn-outline"}
                style={{ padding: "10px 14px", borderRadius: "12px", fontWeight: 700 }}
                onClick={() => {
                  setOriginMode("gps");
                  setSelectedPopupPlaceId(null);
                }}
              >
                Use GPS
              </button>
              <button
                type="button"
                className={selectionTarget === "origin" ? "btn-primary" : "btn-outline"}
                style={{ padding: "10px 14px", borderRadius: "12px", fontWeight: 700 }}
                onClick={() => {
                  setOriginMode("manual");
                  setSelectionTarget("origin");
                  setLocationNotice("Map is ready to confirm the next picked point as your start point.");
                }}
              >
                Pick on map
              </button>
              <button
                type="button"
                className={originMode === "manual" && selectionTarget !== "origin" ? "btn-primary" : "btn-outline"}
                style={{ padding: "10px 14px", borderRadius: "12px", fontWeight: 700 }}
                onClick={() => {
                  setOriginMode("manual");
                  setSelectedPopupPlaceId(null);
                }}
              >
                Enter manually
              </button>
              <button
                type="button"
                className="btn-outline"
                style={{ padding: "10px 14px", borderRadius: "12px", fontWeight: 700 }}
                onClick={handleUseGps}
              >
                Refresh GPS
              </button>
            </div>

            {originMode === "gps" ? (
              <div className="card" style={{ padding: "14px 16px", background: "rgba(255,255,255,0.72)" }}>
                <strong style={{ display: "block", marginBottom: "6px" }}>Current GPS</strong>
                <span style={{ color: "var(--color-text-soft)" }}>
                  {currentLocation
                    ? formatCoordinatePoint(currentLocation)
                    : "Waiting for browser location..."}
                </span>
              </div>
            ) : (
              <input
                value={originInput}
                onChange={(event) => {
                  setOriginPoint(null);
                  setOriginInput(event.target.value);
                }}
                placeholder="Enter your starting point or click the map"
              />
            )}
          </div>

          <div style={{ display: "grid", gap: "12px" }}>
            <strong style={{ color: "var(--color-text)" }}>Destination</strong>
            <div style={{ display: "flex", gap: "10px", flexWrap: "wrap" }}>
              <button
                type="button"
                className={selectionTarget === "destination" ? "btn-primary" : "btn-outline"}
                style={{ padding: "10px 14px", borderRadius: "12px", fontWeight: 700 }}
                onClick={() => {
                  setSelectionTarget("destination");
                  setLocationNotice("Map is ready to confirm the next picked point as your destination.");
                }}
              >
                Pick on map
              </button>
              <button
                type="button"
                className="btn-outline"
                style={{ padding: "10px 14px", borderRadius: "12px", fontWeight: 700 }}
                onClick={() => setSelectionTarget("destination")}
              >
                Pick place marker
              </button>
            </div>
            <input
              value={destinationInput}
              onChange={(event) => {
                setDestinationPoint(null);
                setSelectedPlace(null);
                setDestinationInput(event.target.value);
              }}
              placeholder="Enter a destination or click the map"
            />
            {selectedPlace ? (
              <div className="card" style={{ padding: "14px 16px", background: "rgba(255,255,255,0.72)" }}>
                <strong style={{ display: "block", marginBottom: "6px" }}>Picked place</strong>
                <span style={{ color: "var(--color-text-soft)" }}>
                  {selectedPlace.name} - {selectedPlace.address}
                </span>
              </div>
            ) : null}
          </div>

          <div style={{ display: "grid", gap: "12px" }}>
            <strong style={{ color: "var(--color-text)" }}>Travel mode</strong>
            <div style={{ display: "flex", gap: "10px", flexWrap: "wrap" }}>
              {TRAVEL_MODES.map((mode) => (
                <button
                  key={mode.value}
                  type="button"
                  className={travelMode === mode.value ? "btn-primary" : "btn-outline"}
                  style={{ padding: "10px 14px", borderRadius: "12px", fontWeight: 700 }}
                  onClick={() => setTravelMode(mode.value)}
                >
                  {mode.label}
                </button>
              ))}
            </div>
          </div>

          <div className="card" style={{ padding: "14px 16px", background: "rgba(255,255,255,0.72)" }}>
            <strong style={{ display: "block", marginBottom: "6px" }}>Map selection mode</strong>
            <span style={{ color: "var(--color-text-soft)" }}>
              {selectionTarget === "origin"
                ? "Click anywhere or any place marker to preview it, then use Pick on map to confirm the start point."
                : "Click anywhere or any place marker to preview it, then use Pick on map to confirm the destination."}
            </span>
          </div>

          <div
            className="card"
            style={{
              padding: "14px 16px",
              background: "rgba(255,255,255,0.72)",
              display: "grid",
              gap: "8px",
            }}
          >
            <strong style={{ color: "var(--color-text)" }}>Map markers</strong>
            <span style={{ color: "var(--color-text-soft)" }}>
              Blue = GPS, green = start point, purple = destination, orange = previewed point on the map.
            </span>
          </div>

          <div style={{ display: "flex", gap: "12px", flexWrap: "wrap" }}>
            <button
              type="submit"
              className="btn-primary"
              style={{ padding: "12px 18px", borderRadius: "14px", fontWeight: 700 }}
              disabled={loadingRoute}
            >
              {loadingRoute ? "Calculating..." : "Find Shortest Route"}
            </button>
            <div style={{ alignSelf: "center", color: "var(--color-text-soft)", fontWeight: 600 }}>
              {locationNotice}
            </div>
          </div>

          {routeError ? (
            <div className="card" style={{ padding: "14px 16px", color: "#b91c1c", background: "#fef2f2" }}>
              {routeError}
            </div>
          ) : null}
        </form>
      </Section>

      <Section
        title="Interactive Route Map"
        subtitle="Browse markers freely. Nothing becomes start or destination until you confirm it with Pick on map."
      >
        <MapContainer
          center={mapCenter}
          zoom={13}
          onMapClick={handleMapClick}
          fitBoundsPoints={routeFitBoundsPoints}
        >
          {recommendationPlaces?.length ? (
            <MarkerList
              places={recommendationPlaces}
              onPlaceSelect={(place) => {
                setSelectedPopupPlaceId(place.id);
              }}
              onViewPlace={(place) => {
                if (place._canView === false) {
                  return;
                }
                navigate(`/places/${place.id}`);
              }}
              onSavePlace={handleSavePlace}
              onPickPlace={handleConfirmMapSelection}
              onDismissPlace={clearPreviewSelection}
              primaryActionLabel={
                selectionTarget === "origin" ? "Pick on map: Start" : "Pick on map: Destination"
              }
              selectedPlaceId={selectedPopupPlaceId}
              selectionModeLabel={
                selectionTarget === "origin" ? "Start point mode" : "Destination mode"
              }
              cancelActionLabel="Cancel pin"
            />
          ) : null}

          {originMode === "gps" && currentLocation ? (
            <CircleMarker
              center={[currentLocation.latitude, currentLocation.longitude]}
              radius={gpsMarkerIcon.radius}
              pathOptions={gpsMarkerIcon.pathOptions}
            >
              <Tooltip>Current GPS</Tooltip>
            </CircleMarker>
          ) : null}

          {originMode !== "gps" && originPoint ? (
            <CircleMarker
              center={[originPoint.latitude, originPoint.longitude]}
              radius={originMarkerIcon.radius}
              pathOptions={originMarkerIcon.pathOptions}
            >
              <Tooltip>Start point</Tooltip>
            </CircleMarker>
          ) : null}

          {destinationPoint ? (
            <CircleMarker
              center={[destinationPoint.latitude, destinationPoint.longitude]}
              radius={destinationMarkerIcon.radius}
              pathOptions={destinationMarkerIcon.pathOptions}
            >
              <Tooltip>Destination</Tooltip>
            </CircleMarker>
          ) : null}

          {routeInfo?.path?.length ? (
            <RouteMap path={routeInfo.path} />
          ) : null}
        </MapContainer>
      </Section>

      <Section
        title="Trip Summary"
        subtitle="The route will only be useful after you have actually chosen a start and destination."
      >
        <div className="card" style={{ display: "grid", gap: "16px" }}>
          <div style={{ display: "grid", gap: "8px" }}>
            <p style={{ margin: 0 }}>
              <strong style={{ color: "var(--color-text)" }}>Start:</strong> {startSummary}
            </p>
            <p style={{ margin: 0 }}>
              <strong style={{ color: "var(--color-text)" }}>Destination:</strong> {destinationSummary}
            </p>
          </div>

          {routeInfo ? (
            <>
              <div style={{ display: "flex", gap: "24px", flexWrap: "wrap" }}>
                <div>
                  <div style={{ color: "var(--color-text-soft)", fontSize: "0.9rem" }}>Distance</div>
                  <strong style={{ color: "var(--color-text)" }}>{routeInfo.distance}</strong>
                </div>
                <div>
                  <div style={{ color: "var(--color-text-soft)", fontSize: "0.9rem" }}>Duration</div>
                  <strong style={{ color: "var(--color-text)" }}>{routeInfo.duration}</strong>
                </div>
              </div>

              <div style={{ display: "grid", gap: "10px" }}>
                <div style={{ display: "flex", gap: "12px", flexWrap: "wrap" }}>
                  <button
                    type="button"
                    className="btn-primary"
                    style={{
                      display: "inline-flex",
                      alignItems: "center",
                      gap: "8px",
                      padding: "12px 16px",
                      borderRadius: "14px",
                      fontWeight: 800,
                    }}
                    onClick={handleCompleteRoute}
                    disabled={!canCompleteRoute || savingVisitedPlace}
                    title={
                      canCompleteRoute
                        ? "Mark this route as completed"
                        : "Pick a catalog place as destination first"
                    }
                  >
                    <CheckCircle size={18} />
                    {savingVisitedPlace ? "Saving..." : "Mark as Visited"}
                  </button>
                  <Link
                    to="/social"
                    className="btn-outline"
                    style={{
                      display: "inline-flex",
                      alignItems: "center",
                      padding: "12px 16px",
                      borderRadius: "14px",
                      fontWeight: 800,
                    }}
                  >
                    Write Post
                  </Link>
                </div>

                {routeCompletionMessage ? (
                  <p
                    style={{
                      margin: 0,
                      padding: "12px 14px",
                      borderRadius: "14px",
                      background: "#ecfdf5",
                      color: "#047857",
                      border: "1px solid rgba(16, 185, 129, 0.18)",
                      fontWeight: 700,
                    }}
                  >
                    {routeCompletionMessage}
                  </p>
                ) : null}

                {routeCompletionError ? (
                  <p
                    style={{
                      margin: 0,
                      padding: "12px 14px",
                      borderRadius: "14px",
                      background: "#fef2f2",
                      color: "#b91c1c",
                      border: "1px solid rgba(220, 38, 38, 0.15)",
                      fontWeight: 700,
                    }}
                  >
                    {routeCompletionError}
                  </p>
                ) : null}
              </div>

              {routeInfo.steps?.length ? (
                <div style={{ display: "grid", gap: "12px" }}>
                  {routeInfo.steps.map((step, index) => (
                    <div
                      key={`${step.instructions}-${index}`}
                      style={{
                        padding: "14px 16px",
                        borderRadius: "14px",
                        background: "rgba(255,255,255,0.72)",
                        border: "1px solid var(--color-border)",
                      }}
                    >
                      <strong style={{ display: "block", marginBottom: "6px" }}>
                        Step {index + 1}
                      </strong>
                      <div style={{ color: "var(--color-text)", marginBottom: "6px" }}>
                        {step.instructions}
                      </div>
                      <div style={{ color: "var(--color-text-soft)", fontSize: "0.9rem" }}>
                        {step.distance || "Unknown distance"} - {step.duration || "Unknown duration"}
                      </div>
                    </div>
                  ))}
                </div>
              ) : null}
            </>
          ) : (
            <p style={{ margin: 0 }}>
              Use GPS, type an address, click the map, or pick a marker first. Then calculate the route to see the shortest path summary here.
            </p>
          )}
        </div>
      </Section>
    </div>
  );
}
