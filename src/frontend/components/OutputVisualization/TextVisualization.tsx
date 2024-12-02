// src/components/Visualization/TextVisualization.tsx

import * as React from 'react';
import './TextVisualization.scss';

interface TextVisualizationProps {
    content: string;
}

const TextVisualization: React.FC<TextVisualizationProps> = ({ content }) => {
    return (
        <div className="text-visualization">
            <p>{content}</p>
        </div>
    );
};

export default TextVisualization;
