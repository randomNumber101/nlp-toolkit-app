import * as React from 'react';
import { useEffect, useState } from 'react';
import { FaTrash, FaArrowUp, FaArrowDown, FaChevronRight } from 'react-icons/fa';

import './PipelineConfigScreen.scss';
import { loadStepBlueprint } from '../../utils/pipelineApi';
import { Pipeline, StepBlueprint, StepValues } from '../../types';
import StepConfig from '../../components/StepConfig';
import TextFieldPicker from '../../components/ValuePickers/TextFieldPicker';

interface PipelineConfigScreenProps {
  initialPipe: Pipeline | null;
  blueprintMap: { [key: string]: StepBlueprint };
  onPrevious: () => void;
  onNext: () => void;
  onSavePipeline: (updatedPipeline: Pipeline) => void;
}

const PipelineConfigScreen: React.FC<PipelineConfigScreenProps> = ({
  initialPipe,
  blueprintMap,
  onPrevious,
  onNext,
  onSavePipeline,
}) => {
  // Local state
  const [pipeline, setPipeline] = useState<Pipeline>(initialPipe);
  const [pipelineName, setPipelineName] = useState(pipeline?.name ?? '');
  const [pipelineDescription, setDescription] = useState(pipeline?.description ?? 'No description');
  const [steps, setSteps] = useState<StepValues[]>(pipeline?.steps ?? []);
  const [blueprints] = useState<{ [key: string]: StepBlueprint }>(blueprintMap);

  // For the "fan" approach if you want multiple slides
  const [activeSlide, setActiveSlide] = useState<number>(0);

  // Track which steps are collapsed
  const [collapsedSteps, setCollapsedSteps] = useState<boolean[]>(
    steps.map(() => false)
  );

  useEffect(() => {
    setPipelineName(pipeline?.name);
    setDescription(pipeline?.description ?? 'No description');
    setSteps(pipeline?.steps ?? []);
    // If pipeline changes, re-init collapsed array
    setCollapsedSteps((prev) => steps.map(() => false));
  }, [pipeline]);

  /* ------------------------------
   * Handlers
   * ------------------------------ */
  const handleAddStep = () => {
    const newStep: StepValues = {
      stepId: 'DummyStep', // Ideally generate a unique ID
      values: null,
    };
    setSteps([...steps, newStep]);
    setCollapsedSteps([...collapsedSteps, false]);
  };

  const handleDeleteStep = (index: number) => {
    const newSteps = [...steps];
    newSteps.splice(index, 1);
    setSteps(newSteps);

    const newCollapsed = [...collapsedSteps];
    newCollapsed.splice(index, 1);
    setCollapsedSteps(newCollapsed);
  };

  const handleMoveStep = (index: number, direction: 'up' | 'down') => {
    const newSteps = [...steps];
    const targetIndex = direction === 'up' ? index - 1 : index + 1;
    if (targetIndex < 0 || targetIndex >= newSteps.length) return;
    [newSteps[index], newSteps[targetIndex]] = [newSteps[targetIndex], newSteps[index]];
    setSteps(newSteps);

    // Move collapsed state as well
    const newCollapsed = [...collapsedSteps];
    [newCollapsed[index], newCollapsed[targetIndex]] = [
      newCollapsed[targetIndex],
      newCollapsed[index],
    ];
    setCollapsedSteps(newCollapsed);
  };

  const handleSavePipeline = () => {
    if (pipeline) {
      const updatedPipeline = {
        ...pipeline,
        name: pipelineName,
        description: pipelineDescription,
        steps: steps,
      };
      onSavePipeline(updatedPipeline);
    }
  };

  const handleUpdatedValues = (stepIndex: number, values: StepValues) => {
    const updatedSteps = [...steps];
    updatedSteps[stepIndex] = { ...updatedSteps[stepIndex], ...values };
    setSteps(updatedSteps);
  };

  // Toggle collapse for a step
  const handleToggleCollapse = (index: number) => {
    const newCollapsed = [...collapsedSteps];
    newCollapsed[index] = !newCollapsed[index];
    setCollapsedSteps(newCollapsed);
  };

  // Navigation if you have multiple "slides"
  const goToSlide = (direction: 'prev' | 'next') => {
    if (direction === 'prev') {
      setActiveSlide((prev) => Math.max(prev - 1, 0));
    } else {
      setActiveSlide((prev) => Math.min(prev + 1, 1)); // or however many slides you have
    }
  };

  return (
    <div className="pipeline-config-container">
      {/* Optional nav buttons (like in the Run Screen) */}
      <button
        className="nav-button left"
        onClick={() => goToSlide('prev')}
        disabled={activeSlide === 0}
        aria-label="Previous Slide"
      >
        ‹
      </button>

      <div className="pipeline-config-wrapper">
        {/* The slides container */}
        <div
          className="pipeline-config-slides"
          style={{ transform: `translateX(-${activeSlide * 100}%)` }}
        >
          {/* Slide 1: Basic pipeline details */}
          <div className="config-slide">
            <div className="screen-header">
              <h2>Pipeline Setup</h2>
              <p>Define the pipeline’s name, description, and steps.</p>
            </div>
            <div className="pipeline-details">
              <label>
                Pipeline Name
                <input
                  type="text"
                  value={pipelineName}
                  onChange={(e) => setPipelineName(e.target.value)}
                />
              </label>

              <label>Description</label>
              <TextFieldPicker
                value={pipelineDescription}
                onChange={(newDesc) => setDescription(newDesc)}
              />
            </div>

            <div className="steps-list">
              <h3>Pipeline Steps</h3>
              {steps.map((step, index) => {
                const blueprint = blueprints[step.stepId];
                const isCollapsed = collapsedSteps[index];
                return (
                  <div key={index} className="step-card">
                    <div className="step-header" onClick={() => handleToggleCollapse(index)}>
                      <h4>{blueprint?.name ?? `Step #${index + 1}`}</h4>
                      {/* Chevron icon rotates on collapse */}
                      <FaChevronRight
                        className={`collapse-icon ${isCollapsed ? 'collapsed' : ''}`}
                      />
                    </div>

                    <div
                      className={`step-body ${!isCollapsed ? 'expanded' : ''}`}
                      style={{ maxHeight: isCollapsed ? '0' : '600px' }} // or auto with transitions
                    >
                      <StepConfig
                        blueprint={blueprint}
                        values={step}
                        onUpdate={(vals) => handleUpdatedValues(index, vals)}
                      />
                      <div className="step-actions">
                        <button onClick={() => handleMoveStep(index, 'up')}>
                          <FaArrowUp /> Move Up
                        </button>
                        <button onClick={() => handleMoveStep(index, 'down')}>
                          <FaArrowDown /> Move Down
                        </button>
                        <button onClick={() => handleDeleteStep(index)}>
                          <FaTrash /> Delete
                        </button>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>

            {/* Add Step Button */}
            <button onClick={handleAddStep} className="add-step-button">
              + Add Step
            </button>

            {/* Navigation Buttons at bottom */}
            <div className="navigation">
              <button onClick={onPrevious}>Go back</button>
              <button onClick={handleSavePipeline}>Save</button>
              <button onClick={onNext}>Run Pipeline</button>
            </div>
          </div>

          {/* Slide 2: Potential advanced config or something else */}
          <div className="config-slide">
            <div className="screen-header">
              <h2>Advanced Configuration</h2>
              <p>Additional advanced pipeline options can go here.</p>
            </div>
            {/* Content for Slide 2 */}
          </div>
        </div>
      </div>

      <button
        className="nav-button right"
        onClick={() => goToSlide('next')}
        disabled={activeSlide === 1} // or the last slide index
        aria-label="Next Slide"
      >
        ›
      </button>
    </div>
  );
};

export default PipelineConfigScreen;
