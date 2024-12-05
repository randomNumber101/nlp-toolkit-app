// src/components/RunScreen/RunScreen.tsx

import * as React from 'react';
import { useState, useEffect } from 'react';
import './RunScreen.scss';
import RunStep from '../RunStep/RunStep';
import { StepStatus, StepState } from '../../types/events';
import { Pipeline, StepBlueprint } from '../../types';
import { startRun } from '../../utils/pipelineApi';
import { useBackendEvent } from '../../utils/useBackendEvents';
import { InputHandle } from "../InputScreen/InputScreen";

interface RunScreenProps {
    pipeline: Pipeline;
    blueprints: { [key: string]: StepBlueprint }
    inputHandle: InputHandle;
}

const RunScreen: React.FC<RunScreenProps> = ({ pipeline, blueprints, inputHandle }) => {
    const [runId, setRunId] = useState<string | null>(null);
    const [stepsStatus, setStepsStatus] = useState<StepStatus[]>([]);
    const [activeStepIndex, setActiveStepIndex] = useState<number>(0);
    const [userHasChangedStep, setUserHasChangedStep] = useState<boolean>(false);

    function getHandleData(handle: InputHandle) {
        if (handle.type === "text") {
            return handle.data;
        } else {
            return handle.path;
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
                // Focus on the first step
                setActiveStepIndex(0);
            } else {
                console.error('Run initiation failed.');
            }
        };

        initiateRun();
    }, [pipeline, inputHandle]);

    // Handler for status updates
    const handleStatusUpdate = (event: CustomEvent) => {
        const statusUpdate = event.detail as StepStatus;
        if (runId === statusUpdate.domain.runId && pipeline.id === statusUpdate.domain.pipelineId) {
            setStepsStatus(prevStatuses =>
                prevStatuses.map(status => {
                    if (status.domain.stepIndex === statusUpdate.domain.stepIndex)
                        return statusUpdate;
                    return status;
                })
            );

            // If a step starts running and the user hasn't manually changed steps, update activeStepIndex
            if (statusUpdate.state === StepState.RUNNING && !userHasChangedStep) {
                setActiveStepIndex(statusUpdate.domain.stepIndex);
            }

            // When a step finishes successfully, reset userHasChangedStep to false
            if (statusUpdate.state === StepState.SUCCESS) {
                setUserHasChangedStep(false);
            }
        }
    };

    // Subscribe to status events
    useBackendEvent('stepStatusUpdate', handleStatusUpdate);

    const handlePrev = () => {
        setUserHasChangedStep(true);
        setActiveStepIndex(prev => Math.max(prev - 1, 0));
    };

    const handleNext = () => {
        setUserHasChangedStep(true);
        setActiveStepIndex(prev => Math.min(prev + 1, pipeline.steps.length - 1));
    };

    return (
        <div className="run-screen-container">
            <button
                className="nav-button left"
                onClick={handlePrev}
                disabled={activeStepIndex === 0}
                aria-label="Previous Step"
            >
                ‹
            </button>
            <div className="run-screen-wrapper">
                {runId && stepsStatus.length > 0 && (
                    <div
                        className="run-screen"
                        style={{ transform: `translateX(-${activeStepIndex * 100}%)` }}
                    >
                        {pipeline.steps.map((step, index) => (
                            <RunStep
                                key={index}
                                step={blueprints[step.stepId]}
                                status={stepsStatus[index]}
                                isActive={index === activeStepIndex}
                                runId={runId}
                                stepNumber={index + 1}
                                totalSteps={pipeline.steps.length}
                            />
                        ))}
                    </div>
                )}
            </div>
            <button
                className="nav-button right"
                onClick={handleNext}
                disabled={activeStepIndex === pipeline.steps.length - 1}
                aria-label="Next Step"
            >
                ›
            </button>
        </div>
    );
};

export default RunScreen;
