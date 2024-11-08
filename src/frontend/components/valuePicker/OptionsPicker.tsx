// src/components/OptionsPicker.tsx
import * as React from 'react';

interface OptionsPickerProps {
  options: Array<{ label: string; value: any }>;
  value: any;
  onChange: (value: any) => void;
}

const OptionsPicker: React.FC<OptionsPickerProps> = ({ options, value, onChange }) => (
  <select value={value} onChange={(e) => onChange(e.target.value)}>
    {options.map((option) => (
      <option key={option.value} value={option.value}>
        {option.label}
      </option>
    ))}
  </select>
);

export default OptionsPicker;
