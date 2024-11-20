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
    <div className="boolean-picker">
      <input
        type="checkbox"
        checked={value}
        onChange={handleCheckboxChange}
        className="boolean-checkbox"
      />
    </div>
  );
};

export default CheckboxPicker;
