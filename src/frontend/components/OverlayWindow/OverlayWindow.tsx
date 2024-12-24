import * as React from 'react'
import {ReactNode, useEffect} from "react";
import "./OverlayWindow.scss";

interface OverlayWindowProps {
    isOpen: boolean; // Whether the overlay is open
    onClose: () => void; // Callback for closing the overlay
    children: ReactNode; // Content to render inside the overlay (visualizations or CSV viewer/editor)
    title?: string; // Optional title for the overlay window
}

const OverlayWindow: React.FC<OverlayWindowProps> = ({ isOpen, onClose, children, title }) => {
    useEffect(() => {
        if (isOpen) {
            document.body.classList.add("overlay-active");
        } else {
            document.body.classList.remove("overlay-active");
        }

        return () => {
            document.body.classList.remove("overlay-active");
        };
    }, [isOpen]);

    if (!isOpen) return null;

    return (
        <div className="overlay-container">
            <div className="overlay-backdrop" onClick={onClose}></div>
            <div className="overlay-content">
                <div className="overlay-header">
                    {title && <h2 className="overlay-title">{title}</h2>}
                    <button className="overlay-close" onClick={onClose}>
                        &#x2715;
                    </button>
                </div>
                <div className="overlay-body">{children}</div>
            </div>
        </div>
    );
};

export default OverlayWindow;
