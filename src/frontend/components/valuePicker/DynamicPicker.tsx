// src/components/valuePicker/DynamicPicker.tsx

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
      <div className="complex-picker">
        <div className="complex-header">
          <h4>{parameter.name}</h4>
          <p className="description">{parameter.description}</p>
        </div>
        <div className="complex-body">
          {parameter.picker.parameters.map((innerParam) => (
            <DynamicPicker
              key={innerParam.name}
              parameter={innerParam}
              value={value?.[innerParam.name]}
              onChange={(val) => handleInnerParamChange(innerParam.name, val)}
            />
          ))}
        </div>
      </div>
    );
  }

  switch (parameter.picker?.name) {
    case 'text_field':
      return (
        <div className="picker-container">
          <label>{parameter.name}</label>
          <TextFieldPicker value={value} onChange={onChange} />
          <span className="tooltip">{parameter.description}</span>
        </div>
      );
    case 'slider':
      const min = parameter.picker.values?.min;
      const max = parameter.picker.values?.max;
      const step = parameter.picker.values?.step;
      return (
        <div className="picker-container">
          <label>{parameter.name}</label>
          <SliderPicker value={value} onChange={onChange} min={min} max={max} step={step} />
          <span className="tooltip">{parameter.description}</span>
        </div>
      );
    case 'list':
      return (
        <div className="picker-container">
          <label>{parameter.name}</label>
          <OptionsPicker options={parameter.picker.values?.possibilities || []} value={value} onChange={onChange} />
          <span className="tooltip">{parameter.description}</span>
        </div>
      );
    default:
      return <div>Unsupported picker type: {parameter.picker?.name}</div>;
  }
};

export default DynamicPicker;
