// src/components/RunStep/RunStep.tsx

import * as React from 'react';
import { useState, useEffect } from 'react';
import './RunStep.scss';
import TextVisualization from '../../components/OutputVisualization/TextVisualization';
import LogConsole from '../../components/LogConsole/LogConsole';
import { StepStatus, StepState, VisualizationData, StepLogUpdate, Log } from '../../types/events';
import { StepBlueprint } from '../../types';
import { getRunVisualization } from '../../utils/pipelineApi';
import { useBackendEvent } from '../../utils/useBackendEvents';
import DynamicVisualization from "../../components/OutputVisualization/DynamicVisualization";

interface RunStepProps {
    step: StepBlueprint;
    status: StepStatus;
    isActive: boolean;
    runId: string;
    stepNumber: number;
    totalSteps: number;
}

const RunStep: React.FC<RunStepProps> = ({ step, status, isActive, runId, stepNumber, totalSteps }) => {
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
        const logUpdate = event.detail as StepLogUpdate;
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

    const renderStatus = () => {
        let statusClass = '';
        let statusText = '';

        if (status.state === StepState.SUCCESS) {
            statusClass = 'success';
        } else if (status.state === StepState.FAILED) {
            statusClass = 'failed';
        } else if (status.state === StepState.RUNNING) {
            statusClass = 'running';
        } else {
            statusClass = 'not-started';
        }

        // Convert enum to string and format
        statusText = StepState[status.state].replace('_', ' ').toUpperCase();

        return (
            <div className={`status-message ${statusClass}`}>
                <span className="text">{statusText}</span>
            </div>
        );
    };

    return (
        <div className={`run-step ${isActive ? 'active' : 'inactive'}`}>
            <div className="run-step-content">
                <div className="step-indicator">
                    Step {stepNumber} / {totalSteps}
                </div>
                <div className="step-header">
                    <h3>{step.name}</h3>
                    <p>{step.description}</p>
                </div>
                <div className="step-status">
                    {renderStatus()}
                    {(status.state === StepState.RUNNING || status.state === StepState.NOT_STARTED) && (
                        <div className="progress-bar">
                            <div
                                className="progress"
                                style={{ width: `${status.progress}%` }}
                            ></div>
                        </div>
                    )}
                </div>
                {status.state === StepState.SUCCESS && (
                    <div className="result-group">
                        <h4>Result</h4>
                        <div className="result-area">
                            <DynamicVisualization visualization={visualization}/>
                        </div>
                    </div>
                )}
                {/* Log Console */}
                <LogConsole logs={logs} />
            </div>
        </div>
    );
};

export default RunStep;
