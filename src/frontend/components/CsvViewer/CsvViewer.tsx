import * as React from 'react';
import { useState, useEffect } from 'react';
import Papa from 'papaparse';
import DataTable from 'react-data-table-component';
import './CsvViewer.scss';

interface CsvViewerProps {
  rawData?: string; // For raw file content
  jsonData?: Array<Record<string, any>>; // For JSON-formatted data
  onSaveFile?: (fileName: string) => void; // Optional callback for saving
  maxRows?: number; // Number of rows to display
  maxCellLength?: number; // Max cell content length (optional trimming within cells)
}

const CsvViewer: React.FC<CsvViewerProps> = ({
  rawData,
  jsonData,
  onSaveFile,
  maxRows = 100,
  maxCellLength = 300,
}) => {
  const [data, setData] = useState<Array<Record<string, any>>>([]);

  // Parse CSV when rawData changes.
  useEffect(() => {
    if (jsonData) {
      setData(jsonData);
    } else if (rawData) {
      Papa.parse(rawData, {
        header: true, // Parse header row as keys
        skipEmptyLines: true,
        dynamicTyping: true,
        complete: (result) => {
          setData(result.data as Array<Record<string, any>>);
        },
        error: (error) => {
          console.error('Error parsing CSV:', error);
        },
      });
    }
  }, [rawData, jsonData]);

  // Create the trimmed data that will be passed to the table.
  const trimmedData = data.slice(0, maxRows);
  const remainingRows = data.length - maxRows;

  // Create columns based on the keys of the first row.
  // Generate columns dynamically from the first row of trimmedData.
  // Dynamically generate columns with custom sort functions.
  const columns =
    trimmedData.length > 0
      ? Object.keys(trimmedData[0]).map((key) => {
          const sample = trimmedData[0][key];
          let sortFunction: (rowA: Record<string, any>, rowB: Record<string, any>) => number;

          // Try to convert the sample to a number.
          const sampleAsNumber = Number(sample);
          const isNumber = !isNaN(sampleAsNumber) && sample !== '';

          if (isNumber) {
            sortFunction = (rowA, rowB) => {
              // Convert each to Number to ensure numeric comparison.
              return Number(rowA[key]) - Number(rowB[key]);
            };
          } else if (!isNaN(Date.parse(String(sample))) && String(sample).trim() !== "") {
            // If sample parses as a valid date, sort by date.
            sortFunction = (rowA, rowB) => {
              return new Date(rowA[key]).getTime() - new Date(rowB[key]).getTime();
            };
          } else {
            // Otherwise, perform a lexicographical sort.
            sortFunction = (rowA, rowB) =>
              String(rowA[key]).localeCompare(String(rowB[key]));
          }

          return {
            name: key,
            selector: (row: any) => {
              const value = row[key];
              const stringVal = String(value);
              return stringVal.length > maxCellLength
                ? stringVal.substring(0, maxCellLength) + '...'
                : stringVal;
            },
            sortable: true,
            wrap: true,
            sortFunction,
          };
        })
      : [];



  const customStyles = {
    table: {
      style: {
        tableLayout: 'auto', // Allow dynamic column width calculation
      },
    },
    headRow: {
      style: {
        minHeight: 'unset', // Remove fixed header row height
      },
    },
    headCells: {
      style: {
        paddingLeft: '8px',
        paddingRight: '8px',
        whiteSpace: 'normal', // Allow header text to wrap if needed
      },
    },
    rows: {
      style: {
        minHeight: 'unset', // Remove fixed row height (e.g. default "72px")
        paddingTop: '8px',
        paddingBottom: '8px',
      },
    },
    cells: {
      style: {
        paddingLeft: '8px',
        paddingRight: '8px',
        whiteSpace: 'normal', // Allow cell content to wrap
      },
    },
  };


  return (
    <div className="csv-viewer">
      <DataTable
        columns={columns}
        data={trimmedData}
        pagination={true}
        highlightOnHover={true}
        defaultSortFieldId={1}
        persistTableHead={true}
        customStyles={customStyles}
        fixedHeader={true}
        fixedHeaderScrollHeight={'60vh'}
        // You can override sort icons and other props per your design needs
      />
      {remainingRows > 0 && (
        <p className="remaining-rows">+ {remainingRows} more rows...</p>
      )}
      {onSaveFile && (
        <button className="save-button" onClick={() => onSaveFile('output.csv')}>
          Save
        </button>
      )}
    </div>
  );
};

export default CsvViewer;
