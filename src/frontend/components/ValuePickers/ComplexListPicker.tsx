import * as React from 'react';
import { Parameter } from '../../types';
import DynamicPicker from './DynamicPicker';
import DragAndDrop from '../DragAndDrop/DragAndDrop';
import './ComplexListPicker.scss';
import {InputHandle} from "../../screens/InputScreen/InputScreen";

interface ComplexListPickerProps {
  parameter: Parameter;
  value: any[];
  onChange: (value: any[]) => void;
}

const ComplexListPicker: React.FC<ComplexListPickerProps> = ({ parameter, value = [], onChange }) => {
  const maxLength = parameter.picker?.values?.max_length || Infinity;
  const useDragAndDrop = parameter.picker?.values?.loadable_from_file ?? false;

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
    const newList = value.map((entry, i) => ({
      ...entry,
      extended: i === index ? !entry.extended : false, // Retract other entries when extending one
    }));
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

  // Placeholder for file handling callback.
  // You can implement this function later as needed.
  const handleFile = (fileData: InputHandle) => {
    console.log("File received:", fileData);
    const newEntries = fileData.data.split("\n").map(value => {
      const newEntry = {};
      // Create new entries for each word line
      parameter.picker.parameters.forEach((innerParam) => {
        newEntry[innerParam.name] = innerParam.defaultValue;
      });

      // Set the value of the first inner parameter (must be string type)
      newEntry[parameter.picker.parameters[0].name] = value
      return newEntry
    })
    onChange([...value, ...newEntries])
  };

  // Helper function to replace placeholders in the format string
  const renderFormattedEntry = (format: string, entry: any, index: number) => {
    return format
      .replace(/<#>/g, () => (index + 1).toString())
      .replace(/<value(:\d+)?>/g, (match) => {
        const paramIndex = match.match(/\d+/)?.[0] || '1';
        const paramValue = entry[parameter.picker.parameters[parseInt(paramIndex) - 1]?.name];
        if (paramValue) {
          return renderFirstParamValue(paramValue);
        } else {
          return `<span class="empty-value">empty</span>`;
        }
      });
  };

  return (
    <div className="complex-list-picker">
      <h4>{parameter.name}</h4>
      {parameter.description && (
        <div className="description">
          {parameter.description}
        </div>
      )}
      {useDragAndDrop && (
        <div className="drag-and-drop-area">
          <DragAndDrop onFileDataReceived={handleFile} validExtensions={[".txt"]} />
        </div>
      )}
      <div className="list-body">
        {value.map((entry, index) => {
          const firstParam = parameter.picker.parameters[0];
          const firstParamValue = entry[firstParam.name];
          const isComplex = firstParam.type === 'complex' || firstParam.picker?.name === 'complex_list';
          const format = parameter.picker.values['entry_format'];

          return (
            <div
              key={index}
              className={`list-entry ${entry.extended ? 'extended' : ''}`}
            >
              <div
                className="entry-header"
                onClick={() => toggleExtended(index)}
              >
                <div className="entry-summary">
                  {!isComplex ? (
                    <span className="entry-value">
                      {format ? (
                        <span dangerouslySetInnerHTML={{ __html: renderFormattedEntry(format, entry, index) }} />
                      ) : (
                        firstParamValue ? (
                          renderFirstParamValue(firstParamValue)
                        ) : (
                          <span className="empty-value">empty</span>
                        )
                      )}
                    </span>
                  ) : (
                    <>
                      <span className="entry-index">{index + 1}.</span>
                      <span className="entry-name">{firstParam.name}</span>
                    </>
                  )}
                </div>
                <div className="entry-controls">
                  <button
                    className="extend-button"
                    onClick={(e) => {
                      e.stopPropagation();
                      toggleExtended(index);
                    }}
                  >
                    ✏️
                  </button>
                  <button
                    className="remove-button"
                    onClick={(e) => {
                      e.stopPropagation();
                      handleRemoveEntry(index);
                    }}
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
          <button
            className="add-button"
            onClick={handleAddEntry}
          >
            +
          </button>
        )}
      </div>
    </div>
  );
};

export default ComplexListPicker;
