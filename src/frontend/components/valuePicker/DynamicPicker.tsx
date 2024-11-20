import * as React from 'react';
import TextFieldPicker from './TextFieldPicker';
import SliderPicker from './SliderPicker';
import OptionsPicker from './OptionsPicker';
import CheckboxPicker from './CheckboxPicker'; // Import CheckboxPicker
import { Parameter } from '../../types';
import './DynamicPicker.scss';

interface DynamicPickerProps {
  parameter: Parameter;
  value: any;
  onChange: (value: any) => void;
}

const DynamicPicker: React.FC<DynamicPickerProps> = ({ parameter, value, onChange }) => {
  const defaultValue = value ?? parameter.defaultValue;

  const handleInnerParamChange = (innerName: string, newValue: any) => {
    onChange({ ...value, [innerName]: newValue });
  };

  if (parameter.type === "complex" && parameter.picker && parameter.picker.parameters) {
        return (
          <div className="complex-picker-box">
            <div className="complex-header">
              <h4>{parameter.name}</h4>
              {parameter.description && <p className="description">{parameter.description}</p>}
            </div>
            <div className="complex-body">
              {parameter.picker.parameters.map((innerParam) => (
                <DynamicPicker
                  key={innerParam.name}
                  parameter={innerParam}
                  value={value?.[innerParam.name] ?? parameter.defaultValue?.[innerParam.name]}
                  onChange={(val) => handleInnerParamChange(innerParam.name, val)}
                />
              ))}
            </div>
          </div>
        );
      }


  // Handle different picker types, including complex types
  let pickerElement;
  switch (parameter.picker?.name) {
    case 'text_field':
      pickerElement = <TextFieldPicker value={defaultValue} onChange={onChange} />;
      break;

    case 'slider':
      pickerElement = (
        <SliderPicker
          value={defaultValue}
          onChange={onChange}
          min={parameter.picker.values?.min ?? 0}
          max={parameter.picker.values?.max ?? 100}
          step={parameter.picker.values?.step ?? 1}
        />
      );
      break;

    case 'list':
      pickerElement = (
        <OptionsPicker
          options={parameter.picker.values?.possibilities || []}
          value={defaultValue}
          onChange={onChange}
        />
      );
      break;

    case 'checkbox':
      pickerElement = (
        <CheckboxPicker
          value={!!defaultValue}
          onChange={onChange}
          label={parameter.name}
        />
      );
      break;

    default:
      pickerElement = <div>Unsupported picker type: {parameter.picker?.name}</div>;
  }

  return (
    <div className="picker-container">
      <label className="picker-label">{parameter.name}</label>
      {pickerElement}
      {parameter.description && <span className="tooltip">{parameter.description}</span>}
    </div>
  );
};

export default DynamicPicker;
