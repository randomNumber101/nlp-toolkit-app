import * as React from 'react'
import { useState, useEffect } from "react";
import "./CsvViewer.scss";

interface CsvViewerProps {
    filePath: string; // Path to the CSV file
}

const CsvViewer: React.FC<CsvViewerProps> = ({ filePath }) => {
    const [data, setData] = useState<string[][]>([]);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        // Fetch CSV content (you'll need a backend API to fetch the file)
        fetch(`/api/read_csv?path=${encodeURIComponent(filePath)}`)
            .then((response) => response.json())
            .then((csvData) => setData(csvData))
            .catch((err) => setError("Failed to load CSV file."));
    }, [filePath]);

    if (error) {
        return <div className="csv-error">{error}</div>;
    }

    return (
        <div className="csv-viewer">
            <table className="csv-table">
                <thead>
                    {data.length > 0 && (
                        <tr>
                            {data[0].map((header, idx) => (
                                <th key={idx}>{header}</th>
                            ))}
                        </tr>
                    )}
                </thead>
                <tbody>
                    {data.slice(1).map((row, idx) => (
                        <tr key={idx}>
                            {row.map((cell, cellIdx) => (
                                <td key={cellIdx}>{cell}</td>
                            ))}
                        </tr>
                    ))}
                </tbody>
            </table>
        </div>
    );
};

export default CsvViewer;
