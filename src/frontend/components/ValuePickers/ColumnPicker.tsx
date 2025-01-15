import * as React from 'react';
import { useInputHandleContext } from "../../utils/InputHandleContext";
import OptionsPicker from "./OptionsPicker";
import './ColumnPicker.scss';

interface ColumnPickerProps {
  value: any;
  onChange: (value: any) => void;
}

const ColumnPicker: React.FC<ColumnPickerProps> = ({ value, onChange }) => {
  const inputHandle = useInputHandleContext();
  const defaultValue = value ?? (inputHandle?.headers && inputHandle.headers[0]) ?? "text";
  const options = inputHandle?.headers || ["text"];

  return (
    <div className={"column-picker"}>
        <OptionsPicker options={options} value={defaultValue} onChange={onChange} />
    </div>
  );
};

export default ColumnPicker;
