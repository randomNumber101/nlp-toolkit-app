import * as React from 'react';
import { useInputHandleContext } from "../../utils/InputHandleContext";
import { useState, useEffect } from 'react';
import './ColumnPicker.scss';

interface ColumnPickerProps {
  value: string;
  onChange: (value: string) => void;
}

const ColumnPicker: React.FC<ColumnPickerProps> = ({ value, onChange }) => {
  const inputHandle = useInputHandleContext();
  // Get the available header options from context; default to ['text'] if none
  const options = inputHandle?.headers?.map(header => header.trim()) || ["text"];

  // Determine if the incoming value is not in the available options.
  const isOther = value && options.indexOf(value) == -1;

  // Use component state for the selected option and for a custom "other" text.
  const [selectedOption, setSelectedOption] = useState<string>(isOther ? 'other' : (value || options[0]));
  const [otherValue, setOtherValue] = useState<string>(isOther ? value : '');

  // Update the component state when the parent value changes.
  useEffect(() => {
    const newIsOther = value && options.indexOf(value) == -1;
    setSelectedOption(newIsOther ? 'other' : (value || options[0]));
    setOtherValue(newIsOther ? value : '');
  }, [value, options]);


  const handleSelectChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const newOption = e.target.value;
    setSelectedOption(newOption);
    if (newOption !== 'other') {
      setOtherValue('');
      onChange(newOption);
    } else {
      if (otherValue) {
        onChange(otherValue);
      }
    }
  };

  // Handle changes in the custom text field.
  const handleOtherChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const text = e.target.value;
    setOtherValue(text);
    if (selectedOption === 'other') {
      onChange(text);
    }
  };

  return (
    <div className="column-picker">
      <select className="column-select" value={selectedOption} onChange={handleSelectChange}>
        {options.map(opt => (
          <option key={opt} value={opt}>{opt}</option>
        ))}
        <option className="other" value="other">Choose other...</option>
      </select>
      {selectedOption === 'other' && (
        <input
          type="text"
          className="other-input"
          placeholder="Enter custom value"
          value={otherValue}
          onChange={handleOtherChange}
        />
      )}
    </div>
  );
};

export default ColumnPicker;
