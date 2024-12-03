import * as React from 'react'
import TextVisualization from "./TextVisualization";
import {VisualizationData} from "../../types/events";
import HTMLVisualization from "./HtmlVisualization";

interface DynamicVizProps {
    visualization: VisualizationData;
}

const DynamicVisualization: React.FC<DynamicVizProps> = ({ visualization }) => {
    if (!visualization) return null;
    switch (visualization.type) {
        case 'simple_text':
            return <TextVisualization content={visualization.content.text} />;

        case 'html':
            return <HTMLVisualization content={visualization.content.html} />
        // Future visualization types can be handled here
        default:
            return <div>Unsupported visualization type: {visualization.type}</div>;
    }
};

export default DynamicVisualization;





