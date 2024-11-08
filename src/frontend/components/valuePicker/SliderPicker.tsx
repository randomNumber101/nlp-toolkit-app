// src/components/SliderPicker.tsx
import * as React from 'react';

interface SliderPickerProps {
  value: number;
  onChange: (value: number) => void;
  min: number;
  max: number;
  step: number;
}

const SliderPicker: React.FC<SliderPickerProps> = ({ value, onChange, min, max, step }) => (
  <input
    type="range"
    min={min}
    max={max}
    step={step}
    value={value}
    onChange={(e) => onChange(parseFloat(e.target.value))}
  />
);

export default SliderPicker;
