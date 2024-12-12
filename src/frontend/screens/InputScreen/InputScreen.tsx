// src/components/InputScreen/InputScreen.tsx

import * as React from 'react';
import { useEffect, useState } from 'react';
import TextArea from '../../components/ValuePickers/TextArea';
import DragAndDrop from '../../components/DragAndDrop/DragAndDrop';
import './InputScreen.scss';

interface InputScreenProps {
  preloaded?: InputHandle;
  onGoToPipelineScreen: (input: InputHandle) => void;
}

export interface InputHandle {
  id: string;
  type: 'text' | 'csv';
  preview: string;
  data?: string; // For text inputs and file contents
  name?: string; // Optional, used for file inputs
}

// Converts a string input to an InputHandle
const stringToInputHandle = (input: string): InputHandle => {
  const preview = input.length > 300 ? input.substring(0, 300) + '...' : input;
  return {
    id: crypto.randomUUID(),
    type: 'text',
    data: input,
    preview,
  };
};

// Converts a File object to an InputHandle by reading the entire content for data and the first 300 characters for preview
const fileToInputHandle = async (file: File): Promise<InputHandle> => {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => {
      const content = reader.result as string;
      const preview = content.length > 300 ? content.substring(0, 300) + '...' : content;
      const isCSV = file.name.toLowerCase().endsWith('.csv');
      const type = isCSV ? 'csv' : 'text';
      resolve({
        id: crypto.randomUUID(),
        type: type,
        name: file.name,
        data: content, // Store the full file content here
        preview,
      });
    };
    reader.onerror = () => {
      reject('Failed to read file.');
    };
    // Read the entire file to get the content
    reader.readAsText(file);
  });
};

const InputScreen: React.FC<InputScreenProps> = ({
  preloaded = null,
  onGoToPipelineScreen,
}) => {
  const [input, setInput] = useState<string>(preloaded?.type === 'text' ? preloaded.data || '' : '');
  const [isExpanded, setIsExpanded] = useState<boolean>(false);
  const [errorMessage, setErrorMessage] = useState<string>('');
  const [inputHandle, setInputHandle] = useState<InputHandle | null>(preloaded);
  const [inputType, setInputType] = useState<'text' | 'file'>(
    preloaded?.type === 'csv' ? 'file' : (preloaded?.type === 'text' ? 'text' : 'file')
  ); // To track current input type

  useEffect(() => {
    console.log("New input:", inputHandle)
  }, [inputHandle])

  // Handles the submission of the input
  const handleButtonClick = () => {
    if (inputHandle) {
      onGoToPipelineScreen(inputHandle);
    }
  };

  // Toggles the expansion of the text area
  const toggleExpand = () => {
    setIsExpanded(!isExpanded);
  };

  // Handles changes in the text input
  const handleTextChange = (text: string) => {
    setInput(text);
    setInputHandle(text ? stringToInputHandle(text) : null);
    setErrorMessage('');
  };

  // Handles received file data from DragAndDrop
  const handleFileDataReceived = (handle: InputHandle) => {
    setInput(''); // Clear any existing text input
    setInputHandle(handle);
    setErrorMessage('');
  };

  // Removes the selected file
  const removeFile = () => {
    setInput('');
    setInputHandle(null);
    setErrorMessage('');
  };

  return (
    <div className="input-screen-container">
      <div className="input-methods">
        {/* Toggle between Text and File Input */}
        <div className="input-toggle">
          <button
            className={`toggle-button ${inputType === 'text' ? 'active' : ''}`}
            onClick={() => setInputType('text')}
          >
            Text Input
          </button>
          <button
            className={`toggle-button ${inputType === 'file' ? 'active' : ''}`}
            onClick={() => setInputType('file')}
          >
            File Input
          </button>
        </div>

        {/* Render based on the selected input type */}
        {inputType === 'file' ? (
          <DragAndDrop onFileDataReceived={handleFileDataReceived} />
        ) : (
          <div className={`textarea-container ${isExpanded ? 'expanded' : ''}`}>
            <TextArea
              value={input}
              onChange={handleTextChange}
              rows={isExpanded ? 25 : 6} // Adjust rows based on expansion
              className="input-textarea"
              placeholder="Enter your input here..."
            />
            <button className="expand-button" onClick={toggleExpand}>
              {isExpanded ? 'Collapse' : 'Expand'}
            </button>
          </div>
        )}

        {/* Display file information if a file is uploaded */}
        {inputHandle && inputHandle.type === 'csv' && (
          <div className="file-info">
            <span className="file-icon">📄</span>
            <span className="file-name">{inputHandle.name}</span>
            <button className="remove-file-button" onClick={removeFile}>
              ❌
            </button>
          </div>
        )}
        {inputHandle && inputHandle.type === 'text' && (
          <div className="file-info">
            <span className="file-icon">📝</span>
            <span className="file-name">Text Input</span>
            <button className="remove-file-button" onClick={removeFile}>
              ❌
            </button>
          </div>
        )}

        {/* Display error messages */}
        {errorMessage && <p className="error-message">{errorMessage}</p>}
      </div>

      {/* Submit button */}
      <button
        className={`submit-button ${inputHandle ? '' : 'disabled'}`}
        onClick={handleButtonClick}
        disabled={!inputHandle}
      >
        Choose Pipeline
      </button>
    </div>
  );
};

export default InputScreen;
