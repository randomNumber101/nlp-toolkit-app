import * as React from 'react'

import "./LandingPage.scss"

import { useState } from 'react';

interface Pipeline {
  id: number;
  name: string;
  description: string;
}

interface LandingPageProps {
  onAddPipeline: () => void;
  onSelectPipeline: (pipeline: Pipeline) => void;
  onRunPipeline: (pipeline: Pipeline) => void;
}

const LandingPage = ({onAddPipeline, onSelectPipeline, onRunPipeline} : LandingPageProps) => {
  // Sample data for pipelines, in a real app you would fetch this data or manage it with global state
  const [pipelines, setPipelines] = useState<Pipeline[]>([
    { id: 1, name: 'Sentiment Analysis', description: 'Analyze the sentiment of text data' },
    { id: 2, name: 'Topic Modeling', description: 'Identify topics within a document' },
  ]);

  const handleAddPipeline = () => {
    // Triggered when user clicks "Add Pipeline"
    onAddPipeline();
  };

  const handleSelectPipeline = (pipeline: Pipeline) => {
    // Triggered when user clicks "Configure" on a pipeline
    onSelectPipeline(pipeline);
  };

  const handleRunPipeline = (pipeline: Pipeline) => {
    // Triggered when user clicks "Run" on a pipeline
    onRunPipeline(pipeline);
  };

  return (
    <div className="landing-page">
      <h1>Configured Pipelines</h1>
      <div className="pipeline-list">
        {pipelines.map((pipeline) => (
          <div key={pipeline.id} className="pipeline-card">
            <h3>{pipeline.name}</h3>
            <p>{pipeline.description}</p>
            <div className="pipeline-actions">
              <button onClick={() => handleSelectPipeline(pipeline)} className="configure-button">
                Configure
              </button>
              <button onClick={() => handleRunPipeline(pipeline)} className="run-button">
                Run
              </button>
            </div>
          </div>
        ))}
      </div>
      <button onClick={handleAddPipeline} className="add-pipeline-button">
        + Add New Pipeline
      </button>
    </div>
  );
}

export default LandingPage;
