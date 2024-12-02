// src/components/InputScreen/InputScreen.tsx

import * as React from 'react';
import { useState } from 'react';
import TextArea from '../../components/ValuePickers/TextArea';
import DragAndDrop from '../../components/DragAndDrop/DragAndDrop';
import './InputScreen.scss';

interface InputScreenProps {
  preloaded?: InputHandle;
  onGoToPipelineScreen: (input: InputHandle) => void;
}

export interface InputHandle {
  id: string;
  type: 'text' | 'file';
  preview: string;
  data?: string; // For text inputs
  path?: string; // For file inputs
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

// Converts a File object to an InputHandle by reading the first 300 characters for preview
const fileToInputHandle = async (file: File): Promise<InputHandle> => {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => {
      const content = reader.result as string;
      const preview = content.length > 300 ? content.substring(0, 300) + '...' : content;
      // Assuming pywebview provides access to the full file path
      // If not, you might need to handle this differently
      resolve({
        id: crypto.randomUUID(),
        type: 'file',
        name: file.name,
        path: (file as any).path || '', // Adjust based on your environment
        preview,
      });
    };
    reader.onerror = () => {
      reject('Failed to read file.');
    };
    // Read the entire file to get the first 300 characters for the preview
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
  const [inputType, setInputType] = useState<'text' | 'file'>(preloaded?.type ?? 'file'); // To track current input type

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

  // Handles file uploads and converts them to InputHandle
  const handleFileUpload = async (file: File) => {
    if (file.type === 'text/plain' || file.name.endsWith('.txt')) {
      try {
        const handle = await fileToInputHandle(file);
        setInput(''); // Clear any existing text input
        setInputHandle(handle);
        setErrorMessage('');
      } catch (error) {
        setErrorMessage('Failed to read the file.');
        console.error(error);
      }
    } else {
      setErrorMessage('Only .txt files are accepted.');
    }
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
          <DragAndDrop onFileUpload={handleFileUpload} />
        ) : (
          <div className={`textarea-container ${isExpanded ? 'expanded' : ''}`}>
            <TextArea
              value={input}
              onChange={handleTextChange}
              rows={isExpanded ? 15 : 4} // Adjust rows based on expansion
              className="input-textarea"
              placeholder="Enter your input here..."
            />
            <button className="expand-button" onClick={toggleExpand}>
              {isExpanded ? 'Collapse' : 'Expand'}
            </button>
          </div>
        )}

        {/* Display file information if a file is uploaded */}
        {inputHandle && inputHandle.type === 'file' && (
          <div className="file-info">
            <span className="file-icon">📄</span>
            <span className="file-name">{inputHandle.name}</span>
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
