// src/hooks/useBackendEvents.ts

import { useEffect } from 'react';

type EventHandler = (event: CustomEvent) => void;

export const useBackendEvent = (eventName: string, handler: EventHandler) => {
    useEffect(() => {
        const listener = (e: Event) => {
            handler(e as CustomEvent);
        };

        window.addEventListener(eventName, listener as EventListener);

        return () => {
            window.removeEventListener(eventName, listener as EventListener);
        };
    }, [eventName, handler]);
};

export enum StepState {
    NOT_STARTED,
    RUNNING,
    SUCCESS,
    FAILED
}

export type StepStatus = {
    runId: string
    pipelineId: string
    stepId: string
    state: StepState
}


export const registerStepStatusHandler = (handler : (StepStatus) => void) => {
    useBackendEvent("stepStatusUpdate", (event) => {
        handler(event.detail as StepStatus)
    })
}

export type StepLogUpdate = {
    runId: string
    pipelineId: string
    stepId: string
    logs: string[]
}

export const registerStepLogHandler = (handler : (StepLogUpdate) => void) => {
    useBackendEvent("stepLogUpdate", (event) => {
        handler(event.detail as StepLogUpdate)
    })
}

export default useBackendEvent;
