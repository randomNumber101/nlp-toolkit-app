import * as React from 'react';
import './OptionsPicker.scss';

interface OptionsPickerProps {
  options: Array<string>;
  value: any;
  onChange: (value: any) => void;
}

const OptionsPicker: React.FC<OptionsPickerProps> = ({ options, value, onChange }) => (
  <div className="options-picker-wrapper">
    <select
      value={value}
      onChange={(e) => onChange(e.target.value)}
      className="options-picker"
    >
      {options.map((option) => (
        <option key={option} value={option}>
          {option}
        </option>
      ))}
    </select>
  </div>
);

export default OptionsPicker;
