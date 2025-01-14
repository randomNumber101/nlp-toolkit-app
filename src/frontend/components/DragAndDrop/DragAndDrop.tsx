// src/components/DragAndDrop/DragAndDrop.tsx

import * as React from 'react';
import { useState, useRef, DragEvent } from 'react';
import './DragAndDrop.scss';
import { InputHandle } from '../../screens/InputScreen/InputScreen';

interface DragAndDropProps {
  onFileDataReceived: (inputHandle: InputHandle) => void;
}

const DragAndDrop: React.FC<DragAndDropProps> = ({ onFileDataReceived }) => {
  const [dragActive, setDragActive] = useState<boolean>(false);
  const [errorMessage, setErrorMessage] = useState<string>('');
  const fileInputRef = useRef<HTMLInputElement>(null);

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
      handleFile(files[0]);
    }
  };

  const handleFile = async (file: File) => {
    const validTypes = ['text/plain', 'text/csv'];
    const validExtensions = ['.txt', '.csv'];
    const isValidType = validTypes.indexOf(file.type) != -1;
    const isValidExtension = validExtensions.some(ext => file.name.toLowerCase().endsWith(ext));

    if (isValidType && isValidExtension) {
      try {
        const handle = await fileToInputHandle(file);
        onFileDataReceived(handle);
        setErrorMessage('');
      } catch (error) {
        setErrorMessage('Failed to read the file.');
        console.error(error);
      }
    } else {
      setErrorMessage('Only .txt and .csv files are accepted.');
    }
  };

  const fileToInputHandle = async (file: File): Promise<InputHandle> => {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onload = () => {
        const content = reader.result as string;
        const preview = content.length > 300 ? content.substring(0, 300) + '...' : content;
        const isCSV = file.name.toLowerCase().endsWith('.csv');
        const type = isCSV ? 'csv' : 'text';
        const headers = isCSV ? content.split('\n')[0].split(',') : ["text"];
        resolve({
          id: crypto.randomUUID(),
          type: type,
          name: file.name,
          data: content, // Store the full file content here
          preview,
          headers: headers
        });
      };
      reader.onerror = () => {
        reject('Failed to read file.');
      };
      // Read the entire file to get the content
      reader.readAsText(file);
    });
  };

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      handleFile(e.target.files[0]);
    }
  };

  const handleBrowseFiles = () => {
    fileInputRef.current?.click();
  };

  return (
    <div className="drag-and-drop-container">
      <div
        className={`drop-zone ${dragActive ? 'active' : ''}`}
        onDragEnter={handleDrag}
        onDragOver={handleDrag}
        onDragLeave={handleDrag}
        onDrop={handleDrop}
      >
        <input
          type="file"
          accept=".txt,.csv"
          ref={fileInputRef}
          onChange={handleFileSelect}
          hidden
        />
        <p>
          Drag & Drop your .txt or .csv file here or{' '}
          <span className="browse-text" onClick={handleBrowseFiles}>
            browse
          </span>
        </p>
      </div>
      {errorMessage && <p className="error-message">{errorMessage}</p>}
    </div>
  );
};

export default DragAndDrop;
