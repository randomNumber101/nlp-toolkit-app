import * as React from 'react'

import { useEffect, useRef } from "react";

interface PlotlyVisualizationProps {
    plotlyConfigString: string; // Plotly JSON configuration
}

const PlotlyVisualization: React.FC<PlotlyVisualizationProps> = ({ plotlyConfigString }) => {
    const plotRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
    if (plotRef.current) {
        if ((window as any).Plotly) {
            const plotlyConfig = JSON.parse(plotlyConfigString);
            (window as any).Plotly.newPlot(plotRef.current, plotlyConfig.data, plotlyConfig.layout, plotlyConfig.config);
        } else {
            console.error("Plotly is not loaded.");
        }
    }
}, [plotlyConfigString]);


    return <div ref={plotRef} style={{ width: "100%", height: "100%" }} />;
};

export default PlotlyVisualization;
