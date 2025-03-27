import * as React from 'react';
import { useEffect, useState } from 'react';
import TextArea from '../../components/ValuePickers/TextArea';
import DragAndDrop from '../../components/DragAndDrop/DragAndDrop';
import './InputScreen.scss';
import CsvViewer from "../../components/CsvViewer/CsvViewer";
import OverlayWindow from "../../components/OverlayWindow/OverlayWindow";

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
  headers: string[]; // Optional, used for CSV inputs
}

// Converts a string input to an InputHandle
const stringToInputHandle = (input: string): InputHandle => {
  const preview = input.length > 300 ? input.substring(0, 300) + '...' : input;
  return {
    id: crypto.randomUUID(),
    type: 'text',
    data: input,
    headers: ["text"],
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
    reader.readAsText(file);
  });
};

const InputScreen: React.FC<InputScreenProps> = ({ preloaded = null, onGoToPipelineScreen }) => {
  const [input, setInput] = useState<string>(preloaded?.type === 'text' ? preloaded.data || '' : '');
  const [inputHandle, setInputHandle] = useState<InputHandle | null>(preloaded);
  const [inputType, setInputType] = useState<'text' | 'file'>(
    preloaded?.type === 'csv' ? 'file' : preloaded?.type === 'text' ? 'text' : 'file'
  );
  const [isOverlayOpen, setIsOverlayOpen] = useState<boolean>(false);

  const handleFileDataReceived = (handle: InputHandle) => {
    setInput('');
    setInputHandle(handle);
  };

  const handleTextChange = (text: string) => {
    setInput(text);
    if (text.trim()) {
      setInputHandle(stringToInputHandle(text));
    } else {
      setInputHandle(null);
    }
  };

  const handleButtonClick = () => {
    if (inputHandle) {
      onGoToPipelineScreen(inputHandle);
    }
  };

  const toggleOverlay = () => {
    setIsOverlayOpen(!isOverlayOpen);
  };

  const removeFile = () => {
    setInput('');
    setInputHandle(null);
  };

  return (
    <div className="input-screen-container">
      <div className="input-methods">
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
          <DragAndDrop onFileDataReceived={handleFileDataReceived} validExtensions={[".txt", ".csv"]}/>
        ) : (
          <TextArea
            value={input}
            onChange={handleTextChange}
            rows={6}
            className="input-textarea"
            placeholder="Enter your input here..."
          />
        )}

        {inputHandle && inputHandle.type === 'csv' && (
          <div className="file-info">
            <span className="file-icon">📄</span>
            <span className="file-name">{inputHandle.name}</span>
            <span className="click-to-view" onClick={toggleOverlay}>
              🔎 Click to view
            </span>
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

        <button
          className={`submit-button ${inputHandle ? '' : 'disabled'}`}
          onClick={handleButtonClick}
          disabled={!inputHandle}
        >
          Choose Pipeline
        </button>
      </div>

      <OverlayWindow isOpen={isOverlayOpen} onClose={toggleOverlay} title="CSV Viewer">
        <CsvViewer rawData={inputHandle?.data || ''} maxRows={100} maxCellLength={300} />
      </OverlayWindow>
    </div>
  );
};

export default InputScreen;
