// src/components/RunScreen/RunScreen.tsx

import * as React from 'react';
// src/components/RunScreen/RunScreen.tsx

import { useState, useEffect } from 'react';
import './RunScreen.scss';
import RunStep from '../RunStep/RunStep';
import { StepStatus, StepState } from '../../types/events';
import { Pipeline, StepBlueprint } from '../../types';
import { startRun } from '../../utils/pipelineApi';
import { useBackendEvent } from '../../utils/useBackendEvents';
import {InputHandle} from "../InputScreen/InputScreen";

interface RunScreenProps {
    pipeline: Pipeline;
    blueprints: {[key: string] : StepBlueprint}
    inputHandle: InputHandle;
}

const RunScreen: React.FC<RunScreenProps> = ({ pipeline, blueprints, inputHandle }) => {
    const [runId, setRunId] = useState<string | null>(null);
    const [stepsStatus, setStepsStatus] = useState<StepStatus[]>(
        pipeline.steps.map((step, index) => ({
                    domain: { runId: runId, pipelineId: pipeline.id, stepIndex: index },
                    state: StepState.NOT_STARTED,
                    progress: 0,
                }))
    );
    const [activeStepIndex, setActiveStepIndex] = useState<number>(0);

    function getHandleData(handle: InputHandle) {
        if(handle.type === "text") {
            return handle.data
        }
        else {
            return handle.path
        }
    }

    useEffect(() => {
        // Start the run when the component mounts
        const initiateRun = async () => {
            const newRunId = await startRun(pipeline.id, getHandleData(inputHandle));
            if (newRunId) {
                setRunId(newRunId);
                // Initialize step statuses
                const initialStatuses = pipeline.steps.map((step, index) => ({
                    domain: { runId: newRunId, pipelineId: pipeline.id, stepIndex: index },
                    state: StepState.NOT_STARTED,
                    progress: 0,
                }));
                setStepsStatus(initialStatuses);
            } else {
                console.error('Run initiation failed.');
            }
        };

        initiateRun();
    }, [pipeline, inputHandle, pipeline.steps]);

    // Handler for status updates
    const handleStatusUpdate = (event: CustomEvent) => {
        const statusUpdate = event.detail as StepStatus; // Adjust the type accordingly
        if (runId == statusUpdate.domain.runId && pipeline.id == statusUpdate.domain.pipelineId) {
            console.log("Updating stati:")
            setStepsStatus(prevStatuses =>
                prevStatuses.map(status => {
                    if (!status.domain)
                        console.log("No domain:", status)
                    if (status.domain.stepIndex === statusUpdate.domain.stepIndex)
                        return statusUpdate
                    return status
                })
            );
            // Update active step index
            if (statusUpdate.state === StepState.SUCCESS) {
                setActiveStepIndex(prev => Math.min(prev + 1, pipeline.steps.length - 1));
            }
        }
    };

    // Subscribe to status events
    useBackendEvent('stepStatusUpdate', handleStatusUpdate);

    return (
        <div className="run-screen">
            {pipeline.steps.map((step, index) => (
                <RunStep
                    key={index}
                    step={blueprints[step.stepId]}
                    status={stepsStatus[index]}
                    isActive={index === activeStepIndex}
                    runId={runId || ''}
                />
            ))}
        </div>
    );
};

export default RunScreen;
