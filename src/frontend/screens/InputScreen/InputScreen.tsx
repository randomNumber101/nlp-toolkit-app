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
  loadFull: () => Promise<ReadableStream<Uint8Array>>;
  name?: string; // Optional, used for file inputs
}

const stringToStreamHandle = (input: string): InputHandle => {
  return {
    id: crypto.randomUUID(),
    type: 'text',
    preview: input.substring(0, 300),
    loadFull: () => {
      const encoder = new TextEncoder();
      const uint8array = encoder.encode(input);
      return Promise.resolve(
        new ReadableStream({
          start(controller) {
            controller.enqueue(uint8array);
            controller.close();
          },
        })
      );
    },
  };
};

const fileToStreamHandle = (file: File): InputHandle => {
  return {
    id: crypto.randomUUID(),
    type: 'file',
    name: file.name,
    preview: 'Large file, streaming...',
    loadFull: () => {
      return Promise.resolve(file.stream());
    },
  };
};

const InputScreen: React.FC<InputScreenProps> = ({
  preloaded = null,
  onGoToPipelineScreen,
}) => {
  const [input, setInput] = useState<string>(null);
  const [isExpanded, setIsExpanded] = useState<boolean>(false);
  const [errorMessage, setErrorMessage] = useState<string>('');
  const [inputHandle, setInputHandle] = useState<InputHandle | null>(preloaded);
  const [inputType, setInputType] = useState<'text' | 'file'>(preloaded?.type ?? 'file'); // To track current input type

  const handleButtonClick = () => {
    if (inputHandle) {
      onGoToPipelineScreen(inputHandle);
    }
  };

  const toggleExpand = () => {
    setIsExpanded(!isExpanded);
    // Optionally reset other states if needed
  };

  const handleTextChange = (text: string) => {
    setInput(text);
    setInputHandle(text ? stringToStreamHandle(text) : null);
    setErrorMessage('');
  };

  const handleFileUpload = (file: File) => {
    if (file.type === 'text/plain' || file.name.endsWith('.txt')) {
      setInput('Large file, streaming...');
      setInputHandle(fileToStreamHandle(file));
      setErrorMessage('');
    } else {
      setErrorMessage('Only .txt files are accepted.');
    }
  };

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

        {inputType === 'file' ? (
          <DragAndDrop onFileUpload={handleFileUpload} />
        ) : (
          <div className={`textarea-container ${isExpanded ? 'expanded' : ''} ${inputHandle && inputHandle.type === 'text' ? 'active' : ''}`}>
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

        {inputHandle && inputHandle.type === 'file' && (
          <div className="file-info">
            <span className="file-icon">📄</span>
            <span className="file-name">{inputHandle.name}</span>
            <button className="remove-file-button" onClick={removeFile}>
              ❌
            </button>
          </div>
        )}

        {errorMessage && <p className="error-message">{errorMessage}</p>}
      </div>

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
