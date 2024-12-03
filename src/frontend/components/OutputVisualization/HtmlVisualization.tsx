    // src/components/Visualization/HTMLVisualization.tsx

    import * as React from 'react';

    interface HTMLVisualizationProps {
        content: string
        styling?: string
    }

    const HTMLVisualization: React.FC<HTMLVisualizationProps> = ({ content , styling= ""}) => {

        const html_obj = {
            __html : content
        }

        return (
            <div className="html-visualization-root" dangerouslySetInnerHTML={html_obj}/>
        );
    };

    export default HTMLVisualization;
