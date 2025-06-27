import Lottie from 'lottie-react';
import typingJson from '../assets/typing.json';

export default function ChatLoading() {
  return (
    <div style={{ width: 48, height: 48, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
      <Lottie
        animationData={typingJson}
        loop
        autoplay
        style={{ height: '48px', width: '48px' }}
      />
    </div>
  );
} 