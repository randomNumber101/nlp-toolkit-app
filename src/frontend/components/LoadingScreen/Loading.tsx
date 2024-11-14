import * as React from 'react';
import './Loading.scss';

interface LoadingAnimationProps {
  message: string;
}

const LoadingAnimation: React.FC<LoadingAnimationProps> = ({ message }) => {
  return (
    <div className="loading-container">
      <div className="loader"></div>
      <p className="loading-message">{message}</p>
    </div>
  );
};

export default LoadingAnimation;
