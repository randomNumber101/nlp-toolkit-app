// src/components/DragAndDrop/DragAndDrop.tsx
import * as React from 'react';
import { useState, useRef, DragEvent } from 'react';
import './DragAndDrop.scss';

interface DragAndDropProps {
  onFileUpload: (file: File) => void;
}

const DragAndDrop: React.FC<DragAndDropProps> = ({ onFileUpload }) => {
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

  const handleFile = (file: File) => {
    if (file.type === 'text/plain' || file.name.endsWith('.txt')) {
      onFileUpload(file);
      setErrorMessage('');
    } else {
      setErrorMessage('Only .txt files are accepted.');
    }
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
          accept=".txt"
          ref={fileInputRef}
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
      {errorMessage && <p className="error-message">{errorMessage}</p>}
    </div>
  );
};

export default DragAndDrop;
