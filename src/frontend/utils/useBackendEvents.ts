// src/hooks/useBackendEvents.ts

import { useEffect } from 'react';
import { StepStatus, StepLogUpdate } from '../types/events';

type EventHandler = (event: CustomEvent) => void;

export const useBackendEvent = (eventName: string, handler: EventHandler) => {
    useEffect(() => {
        window.addEventListener(eventName, handler as EventListener);

        return () => {
            window.removeEventListener(eventName, handler as EventListener);
        };
    }, [eventName, handler]);
};
