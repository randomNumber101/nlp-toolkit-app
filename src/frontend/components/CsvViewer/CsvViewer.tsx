import * as React from 'react';
import './CsvViewer.scss';

interface CsvViewerProps {
    data: Array<Record<string, any>>;
}

const CsvViewer: React.FC<CsvViewerProps> = ({ data }) => {
    if (!data || data.length === 0) {
        return <div className="csv-error">No data available to display.</div>;
    }

    console.log(typeof data)
    console.log(typeof data[0])

    const headers = Object.keys(data[0] || {});
    console.log("Headers:", headers);
    console.log("Data:", data);

    return (
        <div className="csv-viewer">
            <table className="csv-table">
                <thead>
                    <tr>
                        {headers.map((header, idx) => (
                            <th key={idx}>{header}</th>
                        ))}
                    </tr>
                </thead>
                <tbody>
                    {data.map((row, rowIndex) => (
                        <tr key={rowIndex}>
                            {headers.map((header, cellIndex) => (
                                <td key={cellIndex}>{row[header]}</td>
                            ))}
                        </tr>
                    ))}
                </tbody>
            </table>
        </div>
    );
};

export default CsvViewer;
