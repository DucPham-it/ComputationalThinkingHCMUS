import React from 'react';
import './navigation.css';

const NavigationStepIcon = ({ type, className = '' }) => {
  const getIcon = () => {
    switch (type?.toLowerCase()) {
      case 'turn-left':
      case 'left':
      case 'rẽ trái':
        return (
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
            <polyline points="9 10 4 15 9 20"></polyline>
            <path d="M20 4v7a4 4 0 0 1-4 4H4"></path>
          </svg>
        );
      case 'turn-right':
      case 'right':
      case 'rẽ phải':
        return (
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
            <polyline points="15 10 20 15 15 20"></polyline>
            <path d="M4 4v7a4 4 0 0 0 4 4h12"></path>
          </svg>
        );
      case 'u-turn':
      case 'quay đầu':
        return (
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
            <path d="M18 20V9a5 5 0 0 0-10 0v11"></path>
            <polyline points="4 16 8 20 12 16"></polyline>
          </svg>
        );
      case 'roundabout':
      case 'vòng xuyến':
        return (
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
            <path d="M12 22a9 9 0 0 0 9-9"></path>
            <path d="M21 13h-4"></path>
            <path d="M3 12a9 9 0 0 0 9 9"></path>
            <path d="M12 21v-4"></path>
            <path d="M12 4a9 9 0 0 0-9 9"></path>
            <path d="M3 13h4"></path>
          </svg>
        );
      case 'destination':
      case 'đến nơi':
        return (
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
            <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"></path>
            <circle cx="12" cy="10" r="3"></circle>
          </svg>
        );
      case 'straight':
      case 'đi thẳng':
      default:
        return (
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
            <line x1="12" y1="20" x2="12" y2="4"></line>
            <polyline points="5 11 12 4 19 11"></polyline>
          </svg>
        );
    }
  };

  return (
    <div className={`nav-step-icon ${className}`}>
      {getIcon()}
    </div>
  );
};

export default NavigationStepIcon;
