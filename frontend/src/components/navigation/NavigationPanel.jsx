import React, { useState, useEffect, useRef } from 'react';
import NavigationBanner from './NavigationBanner';
import NavigationBottomBar from './NavigationBottomBar';
import NavigationOverview from './NavigationOverview';
import './navigation.css';

const NavigationPanel = ({
  steps = [],
  currentStepIndex = 0,
  progress = 0,
  remainingDistance = "0 km",
  remainingTime = "0 phút",
  onEnd = () => { },
  className = ""
}) => {
  const [isVoiceOn, setIsVoiceOn] = useState(true);
  const [showOverview, setShowOverview] = useState(false);

  const currentStep = steps[currentStepIndex] || {
    instruction: 'Đang tải...',
    distance: '',
    type: 'đi thẳng'
  };


  // Formatting helper for decimal distance
  const formatDecimal = (str) => {
    if (!str) return str;
    return str.toString().replace(/(\d+\.\d+)/g, (match) => {
      const num = parseFloat(match);
      return Number.isInteger(num) ? num : parseFloat(num.toFixed(2));
    });
  };

  const formattedRemainingDist = formatDecimal(remainingDistance);
  const formattedStepDist = formatDecimal(currentStep.distance);

  const playTTS = (text) => {
    // Gọi API gTTS ở backend (đảm bảo ra đúng giọng chị Google)
    const url = `http://localhost:8000/api/v1/tts?text=${encodeURIComponent(text)}`;
    const audio = new Audio(url);
    
    // Cố gắng phát âm thanh
    audio.play().catch(e => {
      console.warn("Trình duyệt chặn tự phát âm thanh (autoplay) do chưa có tương tác click:", e);
    });
  };

  const lastSpokenIndex = useRef(-1);

  useEffect(() => {
    if (isVoiceOn && currentStep && currentStep.instruction !== 'Đang tải...') {
      if (lastSpokenIndex.current !== currentStepIndex) {
        lastSpokenIndex.current = currentStepIndex;
        playTTS(currentStep.instruction);
      }
    }
  }, [currentStepIndex, currentStep, isVoiceOn]);

  const toggleVoice = () => {
    const newState = !isVoiceOn;
    setIsVoiceOn(newState);
    
    // Khi người dùng tự tay bấm bật tiếng (có tương tác click chuột), trình duyệt sẽ chắc chắn cho phép phát âm thanh
    if (newState && currentStep && currentStep.instruction !== 'Đang tải...') {
      lastSpokenIndex.current = currentStepIndex;
      playTTS(currentStep.instruction);
    }
  };

  const toggleOverview = () => setShowOverview(!showOverview);

  return (
    <div className={`navigation-panel ${className}`}>
      {/* Clickable banner to show/hide overview */}
      <div onClick={toggleOverview} style={{ cursor: 'pointer', zIndex: 10 }}>
        <NavigationBanner
          instruction={currentStep.instruction}
          distance={formattedStepDist}
          type={currentStep.type}
        />
      </div>

      {showOverview && (
        <div className="nav-overview-container fade-in">
          <NavigationOverview
            steps={steps}
            currentStepIndex={currentStepIndex}
          />
        </div>
      )}

      <NavigationBottomBar
        progress={progress}
        remainingDistance={formattedRemainingDist}
        remainingTime={remainingTime}
        onEnd={onEnd}
        isVoiceOn={isVoiceOn}
        onToggleVoice={toggleVoice}
      />
    </div>
  );
};

export default NavigationPanel;
