import * as React from 'react';
import './CheckboxPicker.scss';

interface CheckboxPickerProps {
  value: boolean | null | undefined; // Allow for null or undefined
  onChange: (value: boolean) => void;
}

const CheckboxPicker: React.FC<CheckboxPickerProps> = ({ value, onChange }) => {
  // Handle null or undefined values by defaulting to false
  const isChecked = value ?? false;

  // Notify the parent of the default value on initialization if value is null or undefined
  React.useEffect(() => {
    if (value == null) {
      onChange(false);
    }
  }, [value, onChange]);

  const handleCheckboxChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    onChange(e.target.checked);
  };

  return (
    <div className="checkbox-picker">
      <label className="switch">
        <input
          type="checkbox"
          checked={isChecked}
          onChange={handleCheckboxChange}
        />
        <span className="slider round"></span>
      </label>
    </div>
  );
};

export default CheckboxPicker;