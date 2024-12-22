import * as React from "react";
import { useEffect, useRef } from "react";

interface PlotlyVisualizationProps {
    content: string; // Plotly JSON configuration
}

const PlotlyVisualization: React.FC<PlotlyVisualizationProps> = ({ content }) => {
    const plotRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        if (plotRef.current && (window as any).Plotly) {
            const plotlyConfig = JSON.parse(content);

            // Add responsive and margin configuration
            plotlyConfig.layout = {
                ...(plotlyConfig.layout || {}),
                autosize: true,
                margin: { t: 40, b: 40, l: 40, r: 40 },
            };
            plotlyConfig.config = {
                ...(plotlyConfig.config || {}),
                responsive: true,
            };

            (window as any).Plotly.newPlot(plotRef.current, plotlyConfig.data, plotlyConfig.layout, plotlyConfig.config);
        }
    }, [content]);

    return <div ref={plotRef} className="plotly-container" />;
};

export default PlotlyVisualization;
