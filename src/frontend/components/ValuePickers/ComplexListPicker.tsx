import * as React from 'react'

import { Parameter } from '../../types';
import DynamicPicker from './DynamicPicker';
import './ComplexListPicker.scss';

interface ComplexListPickerProps {
  parameter: Parameter;
  value: any[];
  onChange: (value: any[]) => void;
}

const ComplexListPicker: React.FC<ComplexListPickerProps> = ({ parameter, value = [], onChange }) => {
  const maxLength = parameter.picker?.values?.max_length || Infinity;

  // Add a new entry to the list
  const handleAddEntry = () => {
    if (value.length < maxLength) {
      const newEntry = {};
      parameter.picker.parameters.forEach((innerParam) => {
        newEntry[innerParam.name] = innerParam.defaultValue;
      });
      onChange([...value, newEntry]);
    }
  };

  // Remove an entry from the list
  const handleRemoveEntry = (index: number) => {
    const newList = value.filter((_, i) => i !== index);
    onChange(newList);
  };

  // Update an entry in the list
  const handleEntryChange = (index: number, updatedEntry: any) => {
    const newList = [...value];
    newList[index] = updatedEntry;
    onChange(newList);
  };

  return (
    <div className="complex-list-picker">
      <div className="list-header">
        <h4>{parameter.name}</h4>
        {parameter.description && <p className="description">{parameter.description}</p>}
        <button
          className="add-button"
          onClick={handleAddEntry}
          disabled={value.length >= maxLength}
        >
          Add Entry
        </button>
      </div>
      <div className="list-body">
        {value.map((entry, index) => (
          <div key={index} className="list-entry">
            <div className="entry-controls">
              <button
                className="remove-button"
                onClick={() => handleRemoveEntry(index)}
              >
                Remove
              </button>
            </div>
            <div className="entry-content">
              {parameter.picker.parameters.map((innerParam) => (
                <DynamicPicker
                  key={innerParam.name}
                  parameter={innerParam}
                  value={entry[innerParam.name]}
                  onChange={(val) => {
                    const updatedEntry = { ...entry, [innerParam.name]: val };
                    handleEntryChange(index, updatedEntry);
                  }}
                />
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default ComplexListPicker;