// src/components/valuePicker/TextArea.tsx
import * as React from 'react';
import './TextArea.scss';

interface TextAreaProps {
  value: string;
  onChange: (value: string) => void;
  rows?: number;
  className?: string;
  placeholder?: string;
}

const TextArea: React.FC<TextAreaProps> = ({
  value,
  onChange,
  rows = 4,
  className = '',
  placeholder = '',
}) => {
  return (
    <textarea
      className={`custom-textarea ${className}`}
      value={value}
      onChange={(e) => onChange(e.target.value)}
      rows={rows}
      placeholder={placeholder}
    />
  );
};

export default TextArea;
