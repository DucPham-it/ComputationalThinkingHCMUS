import React, { useState, useEffect } from 'react';
import MapContainer from '../components/map/MapContainer';
import RouteMap from '../components/map/RouteMap';
import UserPositionMarker from '../components/map/UserPositionMarker';

// Mock data
const mockSteps = [
  { geometry: [{ lat: 10.762622, lng: 106.681043 }, { lat: 10.763422, lng: 106.681543 }] }, // past
  { geometry: [{ lat: 10.763422, lng: 106.681543 }, { lat: 10.764222, lng: 106.682043 }] }, // current
  { geometry: [{ lat: 10.764222, lng: 106.682043 }, { lat: 10.765022, lng: 106.682543 }] }, // future
  { geometry: [{ lat: 10.765022, lng: 106.682543 }, { lat: 10.765822, lng: 106.683043 }] }, // future 2
];

const mockPositions = [
  { lat: 10.763822, lng: 106.681743 },
  { lat: 10.764022, lng: 106.681843 },
  { lat: 10.764222, lng: 106.682043 },
];

export default function TestPerson6Map() {
  const [navMode, setNavMode] = useState(false);
  const [stepIndex, setStepIndex] = useState(1);
  const [posIndex, setPosIndex] = useState(0);

  // Simulated GPS movement
  useEffect(() => {
    if (!navMode) return;
    const interval = setInterval(() => {
      setPosIndex((prev) => (prev + 1) % mockPositions.length);
    }, 2000);
    return () => clearInterval(interval);
  }, [navMode]);

  const currentPos = mockPositions[posIndex];

  return (
    <div style={{ padding: navMode ? '0' : '20px' }}>
      {!navMode && (
        <div style={{ marginBottom: '20px' }}>
          <h2>Test Sandbox - Người 6</h2>
          <button onClick={() => setNavMode(true)}>Start Navigation Mode</button>
          <button onClick={() => setStepIndex((prev) => (prev + 1) % mockSteps.length)}>
            Next Step (Current: {stepIndex})
          </button>
        </div>
      )}
      {navMode && (
        <div style={{ position: 'absolute', top: 10, left: 10, zIndex: 1000, background: 'white', padding: '10px', borderRadius: '8px' }}>
          <button onClick={() => setNavMode(false)}>Stop Navigation Mode</button>
          <button onClick={() => setStepIndex((prev) => (prev + 1) % mockSteps.length)}>
            Next Step (Current: {stepIndex})
          </button>
        </div>
      )}

      <MapContainer 
        navigationMode={navMode} 
        followPosition={navMode ? currentPos : null}
        center={{ lat: 10.763422, lng: 106.681543 }}
        zoom={16}
      >
        <RouteMap 
          navigationMode={navMode}
          steps={mockSteps}
          currentStepIndex={stepIndex}
          path={mockSteps.map(s => s.geometry[0])} // For fallback mode
        />
        {navMode && (
          <UserPositionMarker 
            position={currentPos}
            heading={45}
            accuracy={20}
          />
        )}
      </MapContainer>
    </div>
  );
}
