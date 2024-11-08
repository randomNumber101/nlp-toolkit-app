// src/components/valuePicker/DynamicPicker.tsx

import * as React from 'react';
import TextFieldPicker from './TextFieldPicker';
import SliderPicker from './SliderPicker';
import OptionsPicker from './OptionsPicker';
import { Parameter } from '../../types';

interface DynamicPickerProps {
  parameter: Parameter;
  value: any;
  onChange: (value: any) => void;
}

const DynamicPicker: React.FC<DynamicPickerProps> = ({ parameter, value, onChange }) => {
  if (parameter.type == "complex") {
    return (
      <div className="complex-picker">
        <h4>{parameter.name}</h4>
        <p>{parameter.description}</p>
        {parameter.picker.parameters.map((innerParam) => (
          <DynamicPicker
            key={innerParam.name}
            parameter={innerParam}
            value={value[innerParam.name]}
            onChange={(val) => onChange({ ...value, [innerParam.name]: val })}
          />
        ))}
      </div>
    );
  }

  // Choose the appropriate picker based on parameter type
  switch (parameter.picker.name) {
    case 'text':
      return <TextFieldPicker value={value} onChange={onChange} />;
    case 'slider':
      const min = parameter.picker.values["min"]
      const max = parameter.picker.values["max"]
      const step = parameter.picker.values["step"]
      return <SliderPicker value={value} onChange={onChange} min={min} max={max} step={step} />;
    case 'list':
      return <OptionsPicker options={parameter.picker.values["possibilities"]} value={value} onChange={onChange} />;
    default:
      return <div>Unsupported picker type: {parameter.picker.name}</div>;
  }
};

export default DynamicPicker;
