// src/types/events.ts

export enum StepState {
    NOT_STARTED = 0,
    RUNNING = 1,
    SUCCESS = 2,
    FAILED = 3,
}

export interface NotificationDomain {
    runId: string;
    pipelineId: string;
    stepIndex: number;
}

export interface StepStatus {
    domain: NotificationDomain;
    state: StepState;
    progress: number;
}

export enum LogLevel {
    DEBUG = 0,
    INFO = 1,
    WARN = 2,
    ERROR = 3
}

export interface Log {
    level : LogLevel
    message :string
}

export interface StepLogUpdate {
    domain: NotificationDomain;
    logs: Log[];
}

export interface VisualizationData {
    type: string;
    content: any;
}
