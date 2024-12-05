// src/components/StepperHeader/StepperHeader.tsx

import * as React from 'react';
import './StepperHeader.scss';

interface StepperHeaderProps {
  steps: string[];
  currentStep: number;
  onStepClick: (stepIndex: number) => void;
}

const StepperHeader: React.FC<StepperHeaderProps> = ({ steps, currentStep, onStepClick }) => {
  return (
    <div className="stepper-header">
      {steps.map((step, index) => (
        <div key={index} className="step-container">
          <div
            className={`step ${
              index < currentStep ? 'completed' : index === currentStep ? 'active' : ''
            }`}
            onClick={() => index <= currentStep && onStepClick(index)}
            role="button"
            aria-current={index === currentStep ? 'step' : undefined}
            tabIndex={0}
            onKeyDown={(e) => {
              if (e.key === 'Enter' || e.key === ' ') {
                index <= currentStep && onStepClick(index);
              }
            }}
          >
            <div className="step-number">{index + 1}</div>
            <div className="step-label">{step}</div>
          </div>
          {/* Add the line only if it's not the last step */}
          {index < steps.length - 1 && (
            <div className={`step-line ${index < currentStep ? 'completed' : ''}`}></div>
          )}
        </div>
      ))}
    </div>
  );
};

export default StepperHeader;
