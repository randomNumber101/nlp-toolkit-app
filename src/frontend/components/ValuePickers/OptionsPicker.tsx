// src/components/OptionsPicker.tsx
import * as React from 'react';
import './OptionsPicker.scss'

interface OptionsPickerProps {
  options: Array<string>;
  value: any;
  onChange: (value: any) => void;
}

const OptionsPicker: React.FC<OptionsPickerProps> = ({ options, value, onChange }) => (
  <select value={value} onChange={(e) => onChange(e.target.value)}>
    {options.map((option) => (
      <option key={option} value={option}>
        {option}
      </option>
    ))}
  </select>
);

export default OptionsPicker;
