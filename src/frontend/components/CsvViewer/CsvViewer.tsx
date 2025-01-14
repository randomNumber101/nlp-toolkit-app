import * as React from 'react';
import { useState, useEffect } from 'react';
import Papa from 'papaparse';
import './CsvViewer.scss';

interface CsvViewerProps {
  rawData?: string; // For raw file content
  jsonData?: Array<Record<string, any>>; // For JSON-formatted data
  onSaveFile?: (fileName: string) => void; // Optional callback for saving
  maxRows?: number; // Number of rows to display
  maxCellLength?: number; // Max cell content length
}

const CsvViewer: React.FC<CsvViewerProps> = ({
  rawData,
  jsonData,
  onSaveFile,
  maxRows = 100,
  maxCellLength = 300,
}) => {
  const [data, setData] = useState<Array<Record<string, any>>>([]);
  const [sortedData, setSortedData] = useState<Array<Record<string, any>>>([]);
  const [sortConfig, setSortConfig] = useState<{ key: string; direction: 'asc' | 'desc' } | null>(null);

  useEffect(() => {
    if (jsonData) {
      setData(jsonData);
    } else if (rawData) {
      parseCsv(rawData);
    }
  }, [rawData, jsonData]);

  useEffect(() => {
    if (data && sortConfig) {
      const sorted = [...data].sort((a, b) => compare(a, b, sortConfig.key, sortConfig.direction));
      setSortedData(sorted);
    } else {
      setSortedData(data);
    }
  }, [data, sortConfig]);

  const parseCsv = (rawData: string) => {
    Papa.parse(rawData, {
      header: true, // Treat the first row as headers
      skipEmptyLines: true, // Skip empty lines
      dynamicTyping: true, // Automatically convert numeric values
      complete: (result) => {
        setData(result.data as Array<Record<string, any>>);
      },
      error: (error) => {
        console.error('Error parsing CSV:', error);
      },
    });
  };

  const compare = (a: Record<string, any>, b: Record<string, any>, key: string, direction: 'asc' | 'desc') => {
    const aValue = a[key];
    const bValue = b[key];
    if (typeof aValue === 'number' && typeof bValue === 'number') {
      return direction === 'asc' ? aValue - bValue : bValue - aValue;
    }
    const aString = String(aValue || '');
    const bString = String(bValue || '');
    return direction === 'asc' ? aString.localeCompare(bString) : bString.localeCompare(aString);
  };

  const handleSort = (key: string) => {
    setSortConfig((prev) =>
      prev?.key === key
        ? { key, direction: prev.direction === 'asc' ? 'desc' : 'asc' }
        : { key, direction: 'asc' }
    );
  };

  const trimmedData = sortedData.slice(0, maxRows);
  const remainingRows = data.length - maxRows;

  return (
    <div className="csv-viewer">
      <table className="csv-table">
        <thead>
          <tr>
            {Object.keys(trimmedData[0] || {}).map((header, idx) => (
              <th key={idx} onClick={() => handleSort(header)}>
                {header}
                {sortConfig?.key === header && (sortConfig.direction === 'asc' ? ' 🔼' : ' 🔽')}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {trimmedData.map((row, rowIndex) => (
            <tr key={rowIndex}>
              {Object.keys(row).map((key, cellIndex) => (
                <td key={cellIndex}>
                  {String(row[key]).length > maxCellLength
                    ? String(row[key]).substring(0, maxCellLength) + '...'
                    : row[key]}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
      {remainingRows > 0 && <p className="remaining-rows">+ {remainingRows} more rows...</p>}
      {onSaveFile && (
        <button className="save-button" onClick={() => onSaveFile('output.csv')}>
          Save
        </button>
      )}
    </div>
  );
};

export default CsvViewer;
