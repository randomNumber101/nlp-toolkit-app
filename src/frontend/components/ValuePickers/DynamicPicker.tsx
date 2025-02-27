import * as React from 'react';
import TextFieldPicker from './TextFieldPicker';
import SliderPicker from './SliderPicker';
import OptionsPicker from './OptionsPicker';
import CheckboxPicker from './CheckboxPicker';
import { Parameter } from '../../types';
import './DynamicPicker.scss';
import { useState } from 'react';
import ColumnPicker from "./ColumnPicker";
import ComplexListPicker from "./ComplexListPicker";

interface DynamicPickerProps {
  parameter: Parameter;
  value: any;
  onChange: (value: any) => void;
}

const DynamicPicker: React.FC<DynamicPickerProps> = ({ parameter, value, onChange }) => {
  const defaultValue = value ?? parameter.defaultValue;

  React.useEffect(() => {
    if (value == null) {
      onChange(parameter.defaultValue);
    }
  })

  const handleInnerParamChange = (innerName: string, newValue: any) => {
    onChange({ ...value, [innerName]: newValue });
  };

  const [showTooltip, setShowTooltip] = useState(false);
  const [tooltipPosition, setTooltipPosition] = useState<{ top: number; left: number }>({ top: 0, left: 0 });

  const handleMouseEnter = (e: React.MouseEvent) => {
    const rect = e.currentTarget.getBoundingClientRect();
    setTooltipPosition({ top: rect.top - 10, left: rect.left + rect.width / 2 });
    setShowTooltip(true);
  };

  const handleMouseLeave = () => {
    setShowTooltip(false);
  };

  if (parameter.type === 'complex') {
    const [collapsed, setCollapsed] = useState<boolean>(false);

    return (
      <div className="complex-picker-box">
        <div
          className="complex-header"
          onClick={() => setCollapsed(!collapsed)}
          style={{ cursor: 'pointer' }}
        >
          <h4>{parameter.name}</h4>
          {parameter.description && <p className="description">{parameter.description}</p>}
        </div>
        <div className={`complex-body ${collapsed ? 'collapsed' : 'expanded'}`}>
          {!collapsed &&
            parameter.picker.parameters.map((innerParam) => (
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

  if (parameter.picker?.name === 'complex_list') {
    return (
      <ComplexListPicker
        parameter={parameter}
        value={value}
        onChange={onChange}
      />
    );
  }

  // Handle simple picker types
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
    case 'column_select':
        pickerElement = <ColumnPicker value={defaultValue} onChange={onChange} />;
        break;
    case 'checkbox':
      pickerElement = (
        <CheckboxPicker
          value={defaultValue ?? false}
          onChange={onChange}
          label={parameter.name}
        />
      );
      break;
    default:
      pickerElement = <div>Unsupported picker type: {parameter.picker?.name} with type {parameter.type}</div>;
  }

  return (
    <div
      className="picker-row"
      onMouseEnter={handleMouseEnter}
      onMouseLeave={handleMouseLeave}
    >
      <div className="picker-label">{parameter.name}</div>
      <div className="picker-element">{pickerElement}</div>
      {showTooltip && parameter.description && (
        <div
          className="tooltip"
          style={{ top: tooltipPosition.top, left: tooltipPosition.left }}
        >
          {parameter.description}
        </div>
      )}
    </div>
  );
};

export default DynamicPicker;
