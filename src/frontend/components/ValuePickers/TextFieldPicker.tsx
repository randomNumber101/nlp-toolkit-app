// src/components/TextFieldPicker.tsx
import * as React from 'react';
import './TextFieldPicker.scss'

interface TextFieldPickerProps {
  value: string;
  onChange: (value: string) => void;
  placeholder?: string
}

const TextFieldPicker: React.FC<TextFieldPickerProps> = ({ value, onChange, placeholder }) => {
  return (
    <input
      className="text-field"
      type="text"
      value={value}
      onChange={(e) => onChange(e.target.value)}
      placeholder={placeholder ?? "Enter text"}
    />
  )

}

export default TextFieldPicker;
