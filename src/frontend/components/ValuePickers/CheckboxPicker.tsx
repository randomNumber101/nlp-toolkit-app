import * as React from 'react';
import './CheckboxPicker.scss';

interface CheckboxPickerProps {
  value: boolean;
  onChange: (value: boolean) => void;
}

const CheckboxPicker: React.FC<CheckboxPickerProps> = ({ value, onChange }) => {
  const handleCheckboxChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    onChange(e.target.checked);
  };

  return (
    <div className="checkbox-picker">
      <label className="switch">
        <input
          type="checkbox"
          checked={value}
          onChange={handleCheckboxChange}
        />
        <span className="slider round"></span>
      </label>
    </div>
  );
};

export default CheckboxPicker;
