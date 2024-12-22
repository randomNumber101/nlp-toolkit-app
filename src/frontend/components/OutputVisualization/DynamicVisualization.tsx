import * as React from 'react';
import TextVisualization from "./TextVisualization";
import HTMLVisualization from "./HtmlVisualization";
import MultiVisualization from "./MultiVisualization";
import PropTypes from 'prop-types';
import './DynamicVisualization.scss';
import { VisualizationData } from "../../types/events";
import PlotlyVisualization from "./PlotlyVisualization";

interface DynamicVizProps {
    visualization: VisualizationData;
}

const DynamicVisualization: React.FC<DynamicVizProps> = ({ visualization }) => {
    if (!visualization) return null;

    switch (visualization.type) {
        case 'simple_text':
            return <TextVisualization content={visualization.content.text} />;

        case 'html':
            return <HTMLVisualization content={visualization.content.html} />;

        case 'multi':
            return <MultiVisualization
                visualizations={visualization.content.visualizations}
                renderType={visualization.content.render_type}
                tabNames={visualization.content.tab_names}
            />;

        case 'plotly':
            console.log(visualization.content)
            return <PlotlyVisualization  content={visualization.content.config}/>;

        // Future visualization types can be handled here
        default:
            return <div className="unsupported-viz">Unsupported visualization type: {visualization.type}</div>;
    }
};

export default DynamicVisualization;
