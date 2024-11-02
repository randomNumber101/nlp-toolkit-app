import * as React from 'react'
import { useState } from 'react';

import "./PipelineConfigScreen.scss";

interface Step {
  id: number;
  name: string;
  description: string;
  parameters: Record<string, any>;
}

interface Pipeline {
  id: number;
  name: string;
  description: string;
  steps: Step[];
}

interface PipelineConfigScreenProps {
  pipeline: Pipeline | null;
  onPrevious: () => void;
  onNext: () => void;
  onSavePipeline: (updatedPipeline: Pipeline) => void;
}

const PipelineConfigScreen: React.FC<PipelineConfigScreenProps> = ({ pipeline, onPrevious, onNext, onSavePipeline }) => {
  const [pipelineName, setPipelineName] = useState(pipeline?.name || '');
  const [steps, setSteps] = useState<Step[]>(pipeline?.steps || []);

  // Add a new step to the pipeline
  const handleAddStep = () => {
    const newStep: Step = {
      id: Date.now(), // Generate a unique ID
      name: 'New Step',
      description: 'Describe this step...',
      parameters: {},
    };
    setSteps([...steps, newStep]);
  };

  // Delete a step from the pipeline
  const handleDeleteStep = (stepId: number) => {
    setSteps(steps.filter(step => step.id !== stepId));
  };

  // Move a step up or down in the order
  const handleMoveStep = (index: number, direction: 'up' | 'down') => {
    const newSteps = [...steps];
    const targetIndex = direction === 'up' ? index - 1 : index + 1;
    if (targetIndex < 0 || targetIndex >= steps.length) return; // Out of bounds check
    [newSteps[index], newSteps[targetIndex]] = [newSteps[targetIndex], newSteps[index]];
    setSteps(newSteps);
  };

  const handleSavePipeline = () => {
    if (pipeline) {
      const updatedPipeline = { ...pipeline, name: pipelineName, steps };
      onSavePipeline(updatedPipeline);
    }
  };

  return (
    <div className="pipeline-config-screen">
      <h2>Configure Pipeline</h2>

      {/* Pipeline Name */}
      <label>
        Pipeline Name:
        <input
          type="text"
          value={pipelineName}
          onChange={(e) => setPipelineName(e.target.value)}
        />
      </label>

      {/* Steps List */}
      <div className="steps-list">
        <h3>Steps</h3>
        {steps.map((step, index) => (
          <div key={step.id} className="step-card">
            <h4>{step.name}</h4>
            <p>{step.description}</p>
            <div className="step-actions">
              <button onClick={() => handleMoveStep(index, 'up')}>Move Up</button>
              <button onClick={() => handleMoveStep(index, 'down')}>Move Down</button>
              <button onClick={() => handleDeleteStep(step.id)}>Delete</button>
            </div>
          </div>
        ))}
      </div>

      {/* Add Step Button */}
      <button onClick={handleAddStep} className="add-step-button">+ Add Step</button>

      {/* Save Button */}
      <div className="navigation">
        <button onClick={onPrevious} className="back-button">Go back</button>
        <button onClick={handleSavePipeline} className="next-button">Save</button>
        <button onClick={onNext} className="save-button">Run Pipeline</button>
      </div>
    </div>
  );
};

export default PipelineConfigScreen;


