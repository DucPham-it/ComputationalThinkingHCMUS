import React from 'react';
import './navigation.css';

const NavigationBottomBar = ({ progress, remainingDistance, remainingTime, onEnd, onToggleVoice, isVoiceOn }) => {
  return (
    <div className="nav-bottom-bar slide-up">
      <div className="nav-progress-container">
        <div className="nav-progress-bar" style={{ width: `${progress}%` }}></div>
      </div>
      <div className="nav-bottom-content">
        <div className="nav-bottom-info">
          <div className="nav-time">{remainingTime}</div>
          <div className="nav-distance-total">{remainingDistance}</div>
        </div>
        <div className="nav-bottom-actions">
          <button className={`nav-btn-voice ${isVoiceOn ? 'active' : ''}`} onClick={onToggleVoice}>
            {isVoiceOn ? (
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"></polygon>
                <path d="M15.54 8.46a5 5 0 0 1 0 7.07"></path>
                <path d="M19.07 4.93a10 10 0 0 1 0 14.14"></path>
              </svg>
            ) : (
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"></polygon>
                <line x1="23" y1="9" x2="17" y2="15"></line>
                <line x1="17" y1="9" x2="23" y2="15"></line>
              </svg>
            )}
          </button>
          <button className="nav-btn-end" onClick={onEnd}>Kết thúc</button>
        </div>
      </div>
    </div>
  );
};

export default NavigationBottomBar;
