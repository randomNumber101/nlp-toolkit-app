// src/components/InputScreen/InputScreen.tsx
import * as React from 'react';
import { useState, useRef, DragEvent } from 'react';
import TextArea from '../../components/valuePicker/TextArea';
import './InputScreen.scss';

interface InputScreenProps {
  loadingText?: string;
  onGoToPipelineScreen: (input: string) => void;
}

const InputScreen: React.FC<InputScreenProps> = ({
  loadingText = '',
  onGoToPipelineScreen,
}) => {
  const [input, setInput] = useState(loadingText);
  const [isExpanded, setIsExpanded] = useState(false);
  const [dragActive, setDragActive] = useState(false);
  const [errorMessage, setErrorMessage] = useState('');
  const dropRef = useRef<HTMLDivElement>(null);

  const handleButtonClick = () => {
    onGoToPipelineScreen(input);
  };

  const toggleExpand = () => {
    setIsExpanded(!isExpanded);
    // Reset drag and error states when toggling
    if (!isExpanded) {
      setDragActive(false);
      setErrorMessage('');
    }
  };

  const handleDrag = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleDrop = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    const files = e.dataTransfer.files;
    if (files && files.length > 0) {
      const file = files[0];
      if (file.type === 'text/plain' || file.name.endsWith('.txt')) {
        const reader = new FileReader();
        reader.onload = (event) => {
          const text = event.target?.result;
          if (typeof text === 'string') {
            setInput(text);
            setErrorMessage('');
          }
        };
        reader.readAsText(file);
      } else {
        setErrorMessage('Only .txt files are accepted.');
      }
    }
  };

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (files && files.length > 0) {
      const file = files[0];
      if (file.type === 'text/plain' || file.name.endsWith('.txt')) {
        const reader = new FileReader();
        reader.onload = (event) => {
          const text = event.target?.result;
          if (typeof text === 'string') {
            setInput(text);
            setErrorMessage('');
          }
        };
        reader.readAsText(file);
      } else {
        setErrorMessage('Only .txt files are accepted.');
      }
    }
  };

  const handleBrowseFiles = () => {
    if (dropRef.current) {
      const input = dropRef.current.querySelector('input');
      input?.click();
    }
  };

  return (
    <div className="input-screen-container">
      {!isExpanded && (
        <>
          <div
            className={`drop-zone ${dragActive ? 'active' : ''}`}
            onDragEnter={handleDrag}
            onDragOver={handleDrag}
            onDragLeave={handleDrag}
            onDrop={handleDrop}
            ref={dropRef}
          >
            <input
              type="file"
              accept=".txt"
              onChange={handleFileSelect}
              hidden
            />
            <p>
              Drag & Drop your .txt file here or{' '}
              <span className="browse-text" onClick={handleBrowseFiles}>
                browse
              </span>
            </p>
          </div>

          {/* "OR" Separator */}
          <div className="separator">
            <span>OR</span>
          </div>
        </>
      )}

      {errorMessage && <p className="error-message">{errorMessage}</p>}

      <div className={`textarea-container ${isExpanded ? 'expanded' : ''}`}>
        <TextArea
          value={input}
          onChange={setInput}
          rows={isExpanded ? 15 : 4} // Adjust rows based on expansion
          className="input-textarea"
          placeholder="Enter your input here..."
        />
        <button className="expand-button" onClick={toggleExpand}>
          {isExpanded ? 'Collapse' : 'Expand'}
        </button>
      </div>
      <button className="submit-button" onClick={handleButtonClick}>
        Choose Pipeline
      </button>
    </div>
  );
};

export default InputScreen;
