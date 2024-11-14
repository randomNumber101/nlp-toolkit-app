import * as React from 'react';
import TextFieldPicker from './TextFieldPicker';
import SliderPicker from './SliderPicker';
import OptionsPicker from './OptionsPicker';
import { Parameter } from '../../types';
import './Pickers.scss';

interface DynamicPickerProps {
  parameter: Parameter;
  value: any;
  onChange: (value: any) => void;
}

const DynamicPicker: React.FC<DynamicPickerProps> = ({ parameter, value, onChange }) => {
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
              value={value?.[innerParam.name] ?? parameter.defaultValue?.[innerParam]}
              onChange={(val) => handleInnerParamChange(innerParam.name, val)}
            />
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="picker-container">
      <label className="picker-label">{parameter.name}</label>
      {parameter.picker?.name === 'text_field' && (
        <TextFieldPicker value={value ?? parameter.defaultValue} onChange={onChange} />
      )}
      {parameter.picker?.name === 'slider' && (
        <SliderPicker
          value={value ?? parameter.defaultValue}
          onChange={onChange}
          min={parameter.picker.values?.min ?? 0}
          max={parameter.picker.values?.max ?? 100}
          step={parameter.picker.values?.step ?? 1}
        />
      )}
      {parameter.picker?.name === 'list' && (
        <OptionsPicker options={parameter.picker.values?.possibilities || []} value={value ?? parameter.defaultValue} onChange={onChange} />
      )}
      {parameter.description && <span className="tooltip">{parameter.description}</span>}
    </div>
  );
};

export default DynamicPicker;
