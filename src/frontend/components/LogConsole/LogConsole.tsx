// src/components/LogConsole/LogConsole.tsx

import * as React from "react";
import { useEffect, useRef, useState } from 'react';
import './LogConsole.scss';
import { Log, LogLevel } from "../../types/events";
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faBug, faInfoCircle, faExclamationTriangle, faTimesCircle, faChevronDown, faChevronUp } from '@fortawesome/free-solid-svg-icons';

interface LogConsoleProps {
    logs: Log[];
}

const LogConsole: React.FC<LogConsoleProps> = ({ logs }) => {
    const logContentRef = useRef<HTMLDivElement>(null);
    const [isExpanded, setIsExpanded] = useState<boolean>(true);

    useEffect(() => {
        if (isExpanded && logContentRef.current) {
            logContentRef.current.scrollTop = logContentRef.current.scrollHeight;
        }
    }, [logs, isExpanded]);

    const getLogLevelString = (level: LogLevel): string => {
        return LogLevel[level];
    };

    const getLogIcon = (level: LogLevel) => {
        switch (level) {
            case LogLevel.DEBUG:
                return faBug;
            case LogLevel.INFO:
                return faInfoCircle;
            case LogLevel.WARN:
                return faExclamationTriangle;
            case LogLevel.ERROR:
                return faTimesCircle;
            default:
                return faInfoCircle;
        }
    };

    const toggleExpand = () => {
        setIsExpanded(prev => !prev);
    };

    return (
        <div className={`log-console ${isExpanded ? 'expanded' : 'collapsed'}`}>
            <div className="log-header" onClick={toggleExpand}>
                <h4>Logs</h4>
                <FontAwesomeIcon icon={isExpanded ? faChevronUp : faChevronDown} className="toggle-icon" />
            </div>
            {isExpanded && (
                <div className="log-content" ref={logContentRef}>
                    {logs.map((log, index) => (
                        <div className={`log-entry ${LogLevel[log.level]}`} key={index}>
                            <span className="log-level">
                                <FontAwesomeIcon icon={getLogIcon(log.level)} /> [{getLogLevelString(log.level)}]
                            </span>
                            <span className="log-message">{log.message}</span>
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
};

export default LogConsole;
