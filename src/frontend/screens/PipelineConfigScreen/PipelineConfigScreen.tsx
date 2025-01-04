import * as React from 'react';
import { useEffect, useState } from 'react';
import './PipelineConfigScreen.scss';
import {
  DragDropContext,
  Droppable,
  Draggable,
  DropResult,
} from 'react-beautiful-dnd';

import { Pipeline, StepBlueprint, StepValues } from '../../types';
import OperationBox from '../../components/OperationBox/OperationBox';
import OperationConfigPanel from '../../components/OperationConfigPanel/OperationConfigPanel';
import TextFieldPicker from '../../components/ValuePickers/TextFieldPicker';

interface PipelineConfigScreenProps {
  initialPipe: Pipeline | null;
  blueprintMap: { [key: string]: StepBlueprint };
  onSavePipeline: (updatedPipeline: Pipeline) => void;
  onPrevious: () => void;
  onNext: () => void;
}

const PipelineConfigScreen: React.FC<PipelineConfigScreenProps> = ({
  initialPipe,
  blueprintMap,
  onSavePipeline,
  onPrevious,
  onNext,
}) => {
  const [pipeline, setPipeline] = useState<Pipeline>(initialPipe);
  const [pipelineName, setPipelineName] = useState(pipeline?.name ?? '');
  const [pipelineDescription, setPipelineDescription] = useState(
    pipeline?.description ?? 'No description'
  );
  const [steps, setSteps] = useState<StepValues[]>(pipeline?.steps ?? []);
  const [selectedStepIndex, setSelectedStepIndex] = useState<number | null>(null);

  useEffect(() => {
    setPipelineName(pipeline?.name ?? '');
    setPipelineDescription(pipeline?.description ?? 'No description');
    setSteps(pipeline?.steps ?? []);
  }, [pipeline]);

  const onDragEnd = (result: DropResult) => {
    if (!result.destination) return;

    const reorderedSteps = Array.from(steps);
    const [movedStep] = reorderedSteps.splice(result.source.index, 1);
    reorderedSteps.splice(result.destination.index, 0, movedStep);
    setSteps(reorderedSteps);
  };

  const handleAddOperation = () => {
    const newStep: StepValues = {
      stepId: 'new-step-' + Math.random().toString(36).substr(2, 9),
      values: null,
      uniqueId: `unique-${Date.now()}-${Math.random()}`,
    };
    setSteps([...steps, newStep]);
  };

  return (
    <div className="pipeline-config-screen">
      <div className="pipeline-header">
        <h2>Pipeline Configuration</h2>
        <label>Pipeline Name:</label>
        <input
          type="text"
          value={pipelineName}
          onChange={(e) => setPipelineName(e.target.value)}
        />
        <label>Description:</label>
        <TextFieldPicker
          value={pipelineDescription}
          onChange={(desc) => setPipelineDescription(desc)}
        />
      </div>

      <div className="operations-container">
        <h2>Operations Configurations</h2>
        <DragDropContext onDragEnd={onDragEnd}>
          <Droppable droppableId="operations" direction="horizontal">
            {(provided) => (
              <div
                className="box-list"
                ref={provided.innerRef}
                {...provided.droppableProps}
              >
                {steps.map((step, index) => {
                  const blueprint = blueprintMap[step.stepId];
                  const operationName = blueprint?.name ?? `Operation #${index + 1}`;
                  return (
                    <Draggable
                      key={step.uniqueId}
                      draggableId={step.uniqueId}
                      index={index}
                    >
                      {(provided) => (
                        <div
                          ref={provided.innerRef}
                          {...provided.draggableProps}
                          {...provided.dragHandleProps}
                          onClick={() => setSelectedStepIndex(index === selectedStepIndex ? null : index)}
                        >
                          <OperationBox
                            operationName={operationName}
                            operationDescription={blueprint?.description ?? ''}
                          />
                        </div>
                      )}
                    </Draggable>
                  );
                })}
                {provided.placeholder}
                {/* Add Operation Card */}
                <div className="add-operation-card" onClick={handleAddOperation}>
                  + Add Operation
                </div>
              </div>
            )}
          </Droppable>
        </DragDropContext>
      </div>

      {selectedStepIndex !== null && (
        <div className="config-panel">
          <OperationConfigPanel
            operationName={
              blueprintMap[steps[selectedStepIndex].stepId]?.name ??
              `Operation #${selectedStepIndex + 1}`
            }
            blueprint={blueprintMap[steps[selectedStepIndex].stepId]}
            values={steps[selectedStepIndex]}
            onUpdate={(updatedValues) => {
              const updatedSteps = [...steps];
              updatedSteps[selectedStepIndex] = {
                ...updatedSteps[selectedStepIndex],
                ...updatedValues,
              };
              setSteps(updatedSteps);
            }}
          />
        </div>
      )}

      <div style={{ marginTop: '20px' }}>
        <button onClick={onPrevious}>Back</button>
        <button
          onClick={() =>
            onSavePipeline({
              ...pipeline,
              name: pipelineName,
              description: pipelineDescription,
              steps,
            })
          }
        >
          Save
        </button>
        <button onClick={onNext}>Run Pipeline</button>
      </div>
    </div>
  );
};

export default PipelineConfigScreen;
