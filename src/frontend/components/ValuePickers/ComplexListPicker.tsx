import * as React from 'react';
import { Parameter } from '../../types';
import DynamicPicker from './DynamicPicker';
import './ComplexListPicker.scss';
import * as Console from "console";

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

  // Toggle extended view for an entry
  const toggleExtended = (index: number) => {
    const newList = [...value];
    newList[index].extended = !newList[index].extended;
    onChange(newList);
  };

  // Helper function to render the value of the first parameter
  const renderFirstParamValue = (value: any) => {
    if (typeof value === 'object' && value !== null) {
      // Handle object values (e.g., { word: "example", isRegex: false })
      return JSON.stringify(value);
    }
    return value;
  };

  return (
    <div className="complex-list-picker">
      <div className="list-body">
        {value.map((entry, index) => {
          const firstParam = parameter.picker.parameters[0];
          console.log(firstParam)
          const firstParamValue = entry[firstParam.name];
          const isComplex = firstParam.type === 'complex' || firstParam.picker?.name === 'complex_list';

          return (
            <div key={index} className={`list-entry ${entry.extended ? 'extended' : ''}`}>
              <div className="entry-header">
                <div className="entry-summary">
                  <span className="entry-index">{index + 1}.</span>
                  <span className="entry-name">{firstParam.name}</span>
                  {!isComplex && firstParamValue && (
                    <span className="entry-value">
                      {renderFirstParamValue(firstParamValue)}
                    </span>
                  )}
                </div>
                <div className="entry-controls">
                  <button
                    className="extend-button"
                    onClick={() => toggleExtended(index)}
                  >
                    ✏️
                  </button>
                  <button
                    className="remove-button"
                    onClick={() => handleRemoveEntry(index)}
                  >
                    ❌
                  </button>
                </div>
              </div>
              {entry.extended && (
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
              )}
            </div>
          );
        })}
        {value.length < maxLength && (
          <button className="add-button" onClick={handleAddEntry}>
            +
          </button>
        )}
      </div>
    </div>
  );
};

export default ComplexListPicker;