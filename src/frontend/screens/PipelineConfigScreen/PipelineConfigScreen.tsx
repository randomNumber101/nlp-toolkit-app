import * as React from 'react'
import {useEffect, useState} from 'react';

import "./PipelineConfigScreen.scss";
import StepConfigClass from "../../components/StepConfig";
import {loadStepBlueprint} from "../../utils/pipelineApi";
import {Pipeline, StepBlueprint, StepValues} from "../../types";
import {types} from "sass";
import List = types.List;
import StepConfig from "../../components/StepConfig";


interface PipelineConfigScreenProps {
  pipeline: Pipeline | null;
  blueprintMap: {[key: string] : StepBlueprint}
  onPrevious: () => void;
  onNext: () => void;
  onSavePipeline: (updatedPipeline: Pipeline) => void;
}

const PipelineConfigScreen: React.FC<PipelineConfigScreenProps> = ({ pipeline, blueprintMap, onPrevious, onNext, onSavePipeline }) => {
  const [pipelineName, setPipelineName] = useState(pipeline?.name || '');
  const [steps, setSteps] = useState<StepValues[]>(pipeline?.steps || []);
  const [blueprints, setBlueprintMap] = useState<{[key : string]: StepBlueprint}>(blueprintMap)

  // Add a new step to the pipeline
  const handleAddStep = () => {
    const newStep: StepValues = {
      stepId: "DummyStep", // Generate a unique ID
      values : null
    };
    setSteps([...steps, newStep]);
  };

  // Delete a step from the pipeline
  const handleDeleteStep = (index: number) => {
    setSteps(steps.splice(index, 1));
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

  const handleUpdatedValues = (stepIndex : number, values : StepValues) => {
    const updatedSteps = [... steps]
    updatedSteps[stepIndex] = { ...updatedSteps[stepIndex], values}
    // TODO: Save to file....
    setSteps(updatedSteps)
  }

  console.log("Config Blueprint:")
  console.log(blueprintMap)



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
          <div key={index} className="step-card">
            <StepConfig
                key={index}
                blueprint={blueprints[step.stepId]}
                values={step}
                onUpdate={vs => handleUpdatedValues}
            />
            <div className="step-actions">
              <button onClick={() => handleMoveStep(index, 'up')}>Move Up</button>
              <button onClick={() => handleMoveStep(index, 'down')}>Move Down</button>
              <button onClick={() => handleDeleteStep(index)}>Delete</button>
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


