// src/components/RunScreen/RunScreen.tsx
import * as React from 'react'
import  { useState, useEffect, useCallback } from 'react';
import {Pipeline, StepBlueprint, StepValues} from '../../types';
import { InputHandle } from '../InputScreen/InputScreen';
import './RunScreen.scss';

// Define the props for RunScreen
interface RunScreenProps {
    pipeline: Pipeline;
    inputHandle: InputHandle;
    blueprints: { [name: string]: StepBlueprint };
}

// Enum to represent the status of each step
enum StepStatus {
    NotStarted = 'Not Started',
    Running = 'Running',
    Success = 'Success',
    Failed = 'Failed',
}

// Interface to represent the state of each step
interface StepState {
    status: StepStatus;
    logs: string[];
    output?: string;
}

// RunScreen Component
const RunScreen: React.FC<RunScreenProps> = ({ pipeline, inputHandle, blueprints }) => {
    const [stepsState, setStepsState] = useState<{ [stepId: string]: StepState }>({});
    const [currentStepId, setCurrentStepId] = useState<string | null>(null);
    const [pipelineStatus, setPipelineStatus] = useState<StepStatus>(StepStatus.NotStarted);
    const [isRunning, setIsRunning] = useState<boolean>(false);

    // Initialize steps state
    useEffect(() => {
        const initialState: { [stepId: string]: StepState } = {};
        pipeline.steps.forEach(step => {
            initialState[step.stepId] = {
                status: StepStatus.NotStarted,
                logs: [],
                output: undefined,
            };
        });
        setStepsState(initialState);
    }, [pipeline.steps]);

    // Function to start the pipeline
    const startPipeline = async () => {
        setIsRunning(true);
        setPipelineStatus(StepStatus.Running);
        try {
            const response = await apiStartPipeline(pipeline.id, inputHandle);
            // Assume response contains step execution order or similar info
            // Start polling for status
            pollPipelineStatus(pipeline.id);
        } catch (error) {
            console.error('Error starting pipeline:', error);
            setPipelineStatus(StepStatus.Failed);
            setIsRunning(false);
        }
    };

    // Polling function to fetch pipeline status periodically
    const pollPipelineStatus = useCallback(
        async (pipelineId: string) => {
            const interval = setInterval(async () => {
                try {
                    const status = await apiGetPipelineStatus(pipelineId);
                    if (status === StepStatus.Success || status === StepStatus.Failed) {
                        setPipelineStatus(status);
                        setIsRunning(false);
                        clearInterval(interval);
                    }
                    // Update steps status
                    const steps = await apiGetAllStepsStatus(pipelineId);
                    setStepsState(prevState => {
                        const newState = { ...prevState };
                        steps.forEach(step => {
                            newState[step.stepId] = {
                                ...newState[step.stepId],
                                status: step.status,
                            };
                        });
                        return newState;
                    });
                    // Fetch logs and outputs
                    const currentStep = steps.find(step => step.status === StepStatus.Running);
                    if (currentStep) {
                        setCurrentStepId(currentStep.stepId);
                    }
                    for (const step of steps) {
                        if (step.status === StepStatus.Running || step.status === StepStatus.Success) {
                            const logs = await apiGetStepLogs(pipelineId, step.stepId);
                            const output = step.status === StepStatus.Success ? await apiGetStepOutput(pipelineId, step.stepId) : undefined;
                            setStepsState(prevState => ({
                                ...prevState,
                                [step.stepId]: {
                                    ...prevState[step.stepId],
                                    logs,
                                    output,
                                },
                            }));
                        }
                    }
                } catch (error) {
                    console.error('Error polling pipeline status:', error);
                    clearInterval(interval);
                }
            }, 2000); // Poll every 2 seconds
        },
        []
    );

    return (
        <div className="run-screen">
            <div className="pipeline-steps">
                {pipeline.steps.map(step => (
                    <StepBlock
                        key={step.stepId}
                        step={step}
                        blueprint={blueprints[step.stepId]}
                        state={stepsState[step.stepId]}
                    />
                ))}
            </div>
            <div className="bottom-log-window">
                <CurrentStatus logs={stepsState[currentStepId || '']?.logs || []} />
                <RunButton onRun={startPipeline} disabled={isRunning} />
            </div>
        </div>
    );
};

export default RunScreen;

// Sub-components

interface StepBlockProps {
    step: StepValues;
    blueprint: StepBlueprint;
    state?: StepState;
}

const StepBlock: React.FC<StepBlockProps> = ({ step, blueprint, state }) => {
    return (
        <div className="step-block">
            <div className="step-header">
                <h3>{blueprint.name}</h3>
                <p>{blueprint.description}</p>
                <span className={`status ${state?.status.toLowerCase()}`}>{state?.status}</span>
            </div>
            <div className="step-content">
                {state?.status === StepStatus.Running && <LoadingAnimation />}
                {state?.status === StepStatus.Success && state.output && <OutputViewer output={state.output} />}
                {(state?.status === StepStatus.Running || state?.status === StepStatus.Failed) && (
                    <LogViewer logs={state.logs} />
                )}
            </div>
        </div>
    );
};

interface LogViewerProps {
    logs: string[];
}

const LogViewer: React.FC<LogViewerProps> = ({ logs }) => {
    return (
        <div className="log-viewer">
            <h4>Logs</h4>
            <pre>{logs.join('\n')}</pre>
        </div>
    );
};

interface OutputViewerProps {
    output: string;
}

const OutputViewer: React.FC<OutputViewerProps> = ({ output }) => {
    return (
        <div className="output-viewer">
            <h4>Output</h4>
            <pre>{output}</pre>
        </div>
    );
};

const LoadingAnimation: React.FC = () => {
    return (
        <div className="loading-animation">
            <div className="spinner"></div>
            <p>Running...</p>
        </div>
    );
};

interface CurrentStatusProps {
    logs: string[];
}

const CurrentStatus: React.FC<CurrentStatusProps> = ({ logs }) => {
    return (
        <div className="current-status">
            <h4>Current Status</h4>
            <pre>{logs.join('\n')}</pre>
        </div>
    );
};

interface RunButtonProps {
    onRun: () => void;
    disabled: boolean;
}

const RunButton: React.FC<RunButtonProps> = ({ onRun, disabled }) => {
    return (
        <button className="run-button" onClick={onRun} disabled={disabled}>
            Run
        </button>
    );
};

// Placeholder for backend API functions
// These should be implemented to interact with your backend
const apiStartPipeline = async (pipelineId: string, inputHandle: InputHandle): Promise<void> => {
    // Implement API call to start the pipeline
};

const apiGetPipelineStatus = async (pipelineId: string): Promise<StepStatus> => {
    // Implement API call to get the pipeline status
    return StepStatus.Running;
};

interface StepStatusResponse {
    stepId: string;
    status: StepStatus;
}

const apiGetAllStepsStatus = async (pipelineId: string): Promise<StepStatusResponse[]> => {
    // Implement API call to get all steps' statuses
    return [];
};

const apiGetStepLogs = async (pipelineId: string, stepId: string): Promise<string[]> => {
    // Implement API call to get logs for a specific step
    return [];
};

const apiGetStepOutput = async (pipelineId: string, stepId: string): Promise<string> => {
    // Implement API call to get output for a specific step
    return '';
};
