import * as React from 'react'
import DynamicPicker from './DynamicPicker';
import { Parameter } from '../../types';
import './ListPicker.scss';

interface ListPickerProps {
  parameter: Parameter;
  value: any;
  onChange: (value: any[]) => void;
}

const ListPicker: React.FC<ListPickerProps> = ({ parameter, value, onChange }) => {
  const listValue: any[] = value ?? parameter.defaultValue ?? [];
  const innerParameter = parameter.inner;

  const handleItemChange = (index: number, newValue: any) => {
    const newList = [...listValue];
    newList[index] = newValue;
    onChange(newList);
  };

  const handleAdd = () => {
    const newValue = innerParameter.defaultValue !== undefined ? innerParameter.defaultValue : null;
    onChange([...listValue, newValue]);
  };

  const handleRemove = (index: number) => {
    const newList = listValue.filter((_, i) => i !== index);
    onChange(newList);
  };

  return (
    <div className="list-picker">
      {listValue.map((item, index) => (
        <div key={index} className="list-picker-item">
          <DynamicPicker
            parameter={innerParameter}
            value={item}
            onChange={(newValue) => handleItemChange(index, newValue)}
          />
          <button onClick={() => handleRemove(index)}>Remove</button>
        </div>
      ))}
      <button onClick={handleAdd}>Add</button>
    </div>
  );
};

export default ListPicker;
