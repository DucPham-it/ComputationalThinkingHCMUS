import React from 'react';
import NavigationStepIcon from './NavigationStepIcon';
import './navigation.css';

const NavigationOverview = ({ steps, currentStepIndex }) => {
  return (
    <div className="nav-overview fade-in">
      <ul className="nav-step-list">
        {steps.map((step, index) => {
          const isPast = index < currentStepIndex;
          const isCurrent = index === currentStepIndex;
          
          return (
            <li 
              key={index} 
              className={`nav-step-item ${isPast ? 'past' : ''} ${isCurrent ? 'current' : ''}`}
            >
              <div className="nav-step-item-icon">
                <NavigationStepIcon type={step.type} />
                {index < steps.length - 1 && <div className="nav-step-line"></div>}
              </div>
              <div className="nav-step-item-content">
                <div className="nav-step-item-instruction">{step.instruction}</div>
                <div className="nav-step-item-distance">{step.distance}</div>
              </div>
            </li>
          );
        })}
      </ul>
    </div>
  );
};

export default NavigationOverview;
