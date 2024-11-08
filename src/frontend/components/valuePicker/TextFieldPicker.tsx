// src/components/TextFieldPicker.tsx
import * as React from 'react';

interface TextFieldPickerProps {
  value: string;
  onChange: (value: string) => void;
}

const TextFieldPicker: React.FC<TextFieldPickerProps> = ({ value, onChange }) => (
  <input
    type="text"
    value={value}
    onChange={(e) => onChange(e.target.value)}
    placeholder="Enter text..."
  />
);

export default TextFieldPicker;
