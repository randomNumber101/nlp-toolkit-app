// src/components/LandingPage/LandingPage.tsx

import * as React from 'react';
import { useEffect, useState } from 'react';
import './LandingPage.scss';
import { Pipeline } from '../../types';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faCog } from '@fortawesome/free-solid-svg-icons';

interface LandingPageProps {
  pipelines: Pipeline[];
  onAddPipeline: () => void;
  onSelectPipeline: (pipeline: Pipeline) => void;
  onRunPipeline: (pipeline: Pipeline) => void;
}

const LandingPage: React.FC<LandingPageProps> = ({
  pipelines,
  onAddPipeline,
  onSelectPipeline,
  onRunPipeline,
}) => {
  const handleAddPipeline = () => {
    onAddPipeline();
  };

  const handleSelectPipeline = (pipeline: Pipeline) => {
    onSelectPipeline(pipeline);
  };

  const handleRunPipeline = (pipeline: Pipeline) => {
    onRunPipeline(pipeline);
  };

  return (
    <div className="landing-page">
      <h1>Configured Pipelines</h1>
      <div className="pipeline-list">
        {pipelines.map((pipeline) => (
          <div
            key={pipeline.id}
            className="pipeline-card"
            onClick={() => handleRunPipeline(pipeline)}
          >
            <button
              className="configure-button"
              onClick={(e) => {
                e.stopPropagation(); // Prevent click from triggering parent onClick
                handleSelectPipeline(pipeline);
              }}
              aria-label="Configure Pipeline"
            >
              <FontAwesomeIcon icon={faCog} />
            </button>
            <div className="card-content">
              <h3>{pipeline.name}</h3>
            </div>
            <div className="description">
              <p>{pipeline.description}</p>
            </div>
          </div>
        ))}
      </div>
      <button
        onClick={handleAddPipeline}
        className="add-pipeline-button"
        aria-label="Add New Pipeline"
      >
        +
      </button>
    </div>
  );
};

export default LandingPage;
