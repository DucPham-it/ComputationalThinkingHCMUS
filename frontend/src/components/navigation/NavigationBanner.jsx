import React, { useEffect, useState } from 'react';
import NavigationStepIcon from './NavigationStepIcon';
import './navigation.css';

const NavigationBanner = ({ instruction, distance, type }) => {
  const [pulse, setPulse] = useState(false);

  // Trigger pulse animation when instruction changes
  useEffect(() => {
    setPulse(true);
    const timer = setTimeout(() => setPulse(false), 500);
    return () => clearTimeout(timer);
  }, [instruction, type]);

  return (
    <div className="slide-down">
      <div className={`nav-banner ${pulse ? 'pulse' : ''}`}>
        <div className="nav-banner-icon-container">
          <NavigationStepIcon type={type} className="nav-banner-icon" />
        </div>
        <div className="nav-banner-content">
          <div className="nav-banner-instruction">{instruction}</div>
          <div className="nav-banner-distance">{distance}</div>
        </div>
      </div>
    </div>
  );
};

export default NavigationBanner;
