import * as React from 'react';
import { useState, useEffect } from 'react';
import './SliderPicker.scss';

interface SliderPickerProps {
  value: number | null;
  onChange: (value: number) => void;
  min: number;
  max: number;
  step: number;
}

const SliderPicker: React.FC<SliderPickerProps> = ({ value, onChange, min, max, step }) => {

  const initialValue = value != undefined ? value : min;
  const [displayValue, setDisplayValue] = useState(initialValue);

  useEffect(() => {
    setDisplayValue(initialValue); // Set initial display value to passed value or min
  }, [initialValue]);

  const handleSliderChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newValue = parseFloat(e.target.value);
    setDisplayValue(newValue);
    onChange(newValue);
  };

  return (
    <div className="slider-wrapper">
      <div className="slider-value-box">{displayValue}</div>
      <input
        type="range"
        min={min}
        max={max}
        step={step}
        value={displayValue}
        onChange={handleSliderChange}
        className="slider"
      />
    </div>
  );
};

export default SliderPicker;
