import * as React from 'react'
import {useEffect, useState} from 'react';

import "./LandingPage.scss"
import {Pipeline} from "../../types";
import {listPipelines, listStepBlueprints} from '../../utils/pipelineApi';
import {types} from "sass";
import List = types.List;


interface LandingPageProps {
  pipelines : List[Pipeline]
  onAddPipeline: () => void;
  onSelectPipeline: (pipeline: Pipeline) => void;
  onRunPipeline: (pipeline: Pipeline) => void;
}

const LandingPage = ({pipelines, onAddPipeline, onSelectPipeline, onRunPipeline} : LandingPageProps) => {

  // Sample data for pipelines, in a real app you would fetch this data or manage it with global state

  const handleAddPipeline = () => {
    // Triggered when user clicks "Add Pipeline"
    onAddPipeline();
  };

  const handleSelectPipeline = (pipeline: Pipeline) => {
    // Triggered when user clicks "Configure" on a pipeline
    console.log("User clicked on pipeline:")
    console.log(pipeline)
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
