// src/components/RunStep/RunStep.tsx
import * as React from 'react';
import { useState, useEffect } from 'react';
import './RunStep.scss';
import TextVisualization from '../../components/OutputVisualization/TextVisualization'
import LogConsole from '../../components/LogConsole/LogConsole';
import {StepStatus, StepState, VisualizationData, StepLogUpdate, Log} from '../../types/events';
import { StepBlueprint } from '../../types';
import { getRunVisualization } from '../../utils/pipelineApi';
import { useBackendEvent } from '../../utils/useBackendEvents';

interface RunStepProps {
    step: StepBlueprint;
    status: StepStatus;
    isActive: boolean;
    runId: string;
}

const RunStep: React.FC<RunStepProps> = ({ step, status, isActive, runId }) => {
    const [visualization, setVisualization] = useState<VisualizationData | null>(null);
    const [logs, setLogs] = useState<Log[]>([]);

    // Fetch visualization when step succeeds
    useEffect(() => {
        if (status.state === StepState.SUCCESS) {
            fetchVisualization();
        }
    }, [status]);

    const fetchVisualization = async () => {
        try {
            const vizData = await getRunVisualization(runId, status.domain.stepIndex);
            if (vizData) {
                setVisualization(vizData);
            } else {
                console.error('Visualization data is null.');
            }
        } catch (error) {
            console.error('Error fetching visualization:', error);
        }
    };

    // Handle log updates specific to this step
    const handleLogUpdate = (event: CustomEvent) => {
        const logUpdate = event.detail as StepLogUpdate; // Adjust the type based on actual structure
        console.log(logUpdate)
        if (
            logUpdate.domain.runId === status.domain.runId &&
            logUpdate.domain.pipelineId === status.domain.pipelineId &&
            logUpdate.domain.stepIndex === status.domain.stepIndex
        ) {
            setLogs(prevLogs => [...prevLogs, ...logUpdate.logs]);
        }
    };

    // Subscribe to log events
    useBackendEvent('stepLogUpdate', handleLogUpdate);

    const renderVisualization = () => {
        if (!visualization) return null;
        switch (visualization.type) {
            case 'simple_text':
                return <TextVisualization content={visualization.content.text} />;
            // Future visualization types can be handled here
            default:
                return <div>Unsupported visualization type: {visualization.type}</div>;
        }
    };

    return (
        <div className={`run-step ${isActive ? 'active' : 'inactive'}`}>
            <div className="step-header">
                <h3>{step.name}</h3>
                <p>{step.description}</p>
            </div>
            <div className="step-status">
                {status.state === StepState.RUNNING && (
                    <div className="progress-bar">
                        <div
                            className="progress"
                            style={{ width: `${status.progress}%` }}
                        ></div>
                    </div>
                )}
                {status.state === StepState.SUCCESS && (
                    <span className="status success">Success</span>
                )}
                {status.state === StepState.FAILED && (
                    <span className="status failed">Failed</span>
                )}
                {status.state === StepState.NOT_STARTED && (
                    <span className="status not-started">Not Started</span>
                )}
            </div>
            {status.state === StepState.SUCCESS && (
                <div className="step-visualization">
                    {renderVisualization()}
                </div>
            )}
            {/* Log Console */}
            <LogConsole logs={logs} />
        </div>
    );
};

export default RunStep;
