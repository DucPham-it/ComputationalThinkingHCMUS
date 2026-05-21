import React, { useState, useEffect } from 'react';
import NavigationPanel from '../components/navigation/NavigationPanel';

const NavigationTestPage = () => {
  // Dữ liệu giả lập (mock data) các bước chỉ đường
  const mockSteps = [
    { instruction: 'Đi thẳng trên đường Lê Lợi', distance: '200m', type: 'đi thẳng' },
    { instruction: 'Rẽ phải vào đường Nguyễn Huệ', distance: '50m', type: 'rẽ phải' },
    { instruction: 'Đi vòng xuyến và rẽ vào lối ra thứ 2', distance: '100m', type: 'vòng xuyến' },
    { instruction: 'Rẽ trái vào đường Tôn Đức Thắng', distance: '500m', type: 'rẽ trái' },
    { instruction: 'Quay đầu tại ngã tư', distance: '10m', type: 'quay đầu' },
    { instruction: 'Bạn đã đến nơi', distance: '0m', type: 'đến nơi' }
  ];

  const [currentIndex, setCurrentIndex] = useState(0);

  // Tự động chuyển bước sau mỗi 3 giây để test UI
  useEffect(() => {
    const timer = setInterval(() => {
      setCurrentIndex((prev) => (prev < mockSteps.length - 1 ? prev + 1 : 0));
    }, 3000);
    return () => clearInterval(timer);
  }, [mockSteps.length]);

  // Tính toán progress giả lập
  const progress = ((currentIndex + 1) / mockSteps.length) * 100;

  return (
    <div style={{ position: 'relative', width: '100vw', height: '100vh', backgroundColor: '#e0e0e0' }}>
      {/* Nền bản đồ giả lập */}
      <div style={{ padding: '20px', textAlign: 'center', color: '#666' }}>
        <h2>Bản đồ ở phía dưới đây...</h2>
        <p>Giao diện NavigationPanel sẽ hiển thị đè lên trên bản đồ.</p>
      </div>

      <NavigationPanel 
        steps={mockSteps}
        currentStepIndex={currentIndex}
        progress={progress}
        remainingDistance={`${(1.5 - currentIndex * 0.3).toFixed(1)} km`}
        remainingTime={`${15 - currentIndex * 3} phút`}
        onEnd={() => alert("Đã bấm Kết thúc hành trình!")}
      />
    </div>
  );
};

export default NavigationTestPage;
