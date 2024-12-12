// src/components/MultiVisualization/MultiVisualization.tsx

import * as React from 'react';
import { useState } from 'react';
import DynamicVisualization from "./DynamicVisualization";
import PropTypes from 'prop-types';
import './MultiVisualization.scss';
import { VisualizationData } from "../../types/events";

// Assuming VisualizationData is an array of VisualizationData items
interface MultiVizProps {
    visualizations: VisualizationData[];
}

const MultiVisualization: React.FC<MultiVizProps> = ({ visualizations }) => {
    const [currentIndex, setCurrentIndex] = useState(0);

    const goToPrevious = () => {
        setCurrentIndex((prevIndex) => (prevIndex === 0 ? visualizations.length - 1 : prevIndex - 1));
    };

    const goToNext = () => {
        setCurrentIndex((prevIndex) => (prevIndex === visualizations.length - 1 ? 0 : prevIndex + 1));
    };

    const goToIndex = (index: number) => {
        setCurrentIndex(index);
    };

    if (!visualizations || visualizations.length === 0) return null;

    return (
        <div className="multi-visualization">
            <div className="visualization-content">
                <DynamicVisualization visualization={visualizations[currentIndex]} />
            </div>
            <div className="navigation-arrows">
                <button onClick={goToPrevious} className="nav-button left">
                    &#8592;
                </button>
                <button onClick={goToNext} className="nav-button right">
                    &#8594;
                </button>
            </div>
            <div className="tabs">
                {visualizations.map((viz, index) => (
                    <button
                        key={index}
                        className={`tab-button ${index === currentIndex ? 'active' : ''}`}
                        onClick={() => goToIndex(index)}
                    >
                        {index + 1}
                    </button>
                ))}
            </div>
        </div>
    );
};

export default MultiVisualization;
