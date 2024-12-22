import * as React from 'react';
import { useState } from 'react';
import DynamicVisualization from "./DynamicVisualization";
import './MultiVisualization.scss';
import { VisualizationData } from "../../types/events";

interface MultiVizProps {
    visualizations: VisualizationData[];
    renderType: string; // "numbered" or "tabbed"
    tabNames?: string[];
}

const MultiVisualization: React.FC<MultiVizProps> = ({ visualizations, renderType, tabNames = [] }) => {
    const [currentIndex, setCurrentIndex] = useState(0);

    const goToPrevious = () => {
        setCurrentIndex((prevIndex) => (prevIndex === 0 ? visualizations.length - 1 : prevIndex - 1));
    };

    const goToNext = () => {
        setCurrentIndex((prevIndex) => (prevIndex === visualizations.length - 1 ? 0 : prevIndex + 1));
    };

    const visibleRange = () => {
        const start = Math.max(currentIndex - 5, 0);
        const end = Math.min(currentIndex + 5, visualizations.length);
        return { start, end };
    };

    const { start, end } = visibleRange();

    return (
        <div className="multi-visualization">
            <div className="visualization-content">
                <DynamicVisualization visualization={visualizations[currentIndex]} />
            </div>
            <div className="navigation-arrows">
                <button onClick={goToPrevious} className="nav-button left">
                    &#x2190;
                </button>
                <button onClick={goToNext} className="nav-button right">
                    &#x2192;
                </button>
            </div>
            <div className="tabs">
                {renderType === "numbered" ? (
                    // Numbered View
                    visualizations.slice(start, end).map((_, index) => {
                        const absoluteIndex = start + index;
                        return (
                            <button
                                key={absoluteIndex}
                                className={`number-tab ${absoluteIndex === currentIndex ? 'active' : ''}`}
                                onClick={() => setCurrentIndex(absoluteIndex)}
                            >
                                {absoluteIndex + 1}
                            </button>
                        );
                    })
                ) : (
                    // Tabbed View
                    visualizations.slice(start, end).map((_, index) => {
                        const absoluteIndex = start + index;
                        return (
                            <button
                                key={absoluteIndex}
                                className={`tab-button ${absoluteIndex === currentIndex ? 'active' : ''}`}
                                onClick={() => setCurrentIndex(absoluteIndex)}
                            >
                                {tabNames[absoluteIndex] || `Tab ${absoluteIndex + 1}`}
                            </button>
                        );
                    })
                )}
            </div>
        </div>
    );
};

export default MultiVisualization;
