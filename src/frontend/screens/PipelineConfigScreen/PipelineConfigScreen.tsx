// src/components/PipelineConfigScreen/PipelineConfigScreen.tsx

import * as React from 'react';
import { useEffect, useMemo, useRef, useState } from 'react';
import './PipelineConfigScreen.scss';
import { DragDropContext, Droppable, Draggable, DropResult } from 'react-beautiful-dnd';
import { Pipeline, StepBlueprint, StepValues } from '../../types';
import OperationBox from '../../components/OperationBox/OperationBox';
import TextFieldPicker from '../../components/ValuePickers/TextFieldPicker';
import OperationConfigPanel from '../../components/OperationConfigPanel/OperationConfigPanel';
import { FaSave, FaArrowLeft, FaPlay, FaFileAlt } from 'react-icons/fa';
import { useBlueprintContext } from "../../utils/BlueprintContext";
import { listToMap } from "../../utils/functional";
import StepConfig from "../../components/StepConfig/StepConfig";
import CsvViewer from "../../components/CsvViewer/CsvViewer";
import OverlayWindow from "../../components/OverlayWindow/OverlayWindow";
import {InputHandle} from "../InputScreen/InputScreen";
import {useInputHandleContext} from "../../utils/InputHandleContext";

interface PipelineConfigScreenProps {
  initialPipe: Pipeline | null;
  onSavePipeline: (updatedPipeline: Pipeline) => void;
  onPrevious: () => void;
  onNext: () => void;
  outputFileName: string;
}

const PipelineConfigScreen: React.FC<PipelineConfigScreenProps> = ({
  initialPipe,
  onSavePipeline,
  onPrevious,
  onNext,
  outputFileName,
}) => {
  const [pipeline, setPipeline] = useState<Pipeline>(initialPipe);
  const [pipelineName, setPipelineName] = useState(pipeline?.name ?? '');
  const [pipelineDescription, setPipelineDescription] = useState(pipeline?.description ?? 'No description');
  const [steps, setSteps] = useState<StepValues[]>(pipeline?.steps ?? []);
  const [selectedStepIndex, setSelectedStepIndex] = useState<number | null>(null);
  const [isDragging, setIsDragging] = useState(false);
  const [showSaved, setShowSaved] = useState(false);
  const [showOperationToolbox, setShowOperationToolbox] = useState(false);
  const [showInputCsv, setShowInputCsv] = useState(false);
  const inputHandle = useInputHandleContext();

  const toolboxRef = useRef<HTMLDivElement>(null);
  const addOperationRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    setPipelineName(pipeline?.name ?? '');
    setPipelineDescription(pipeline?.description ?? 'No description');
    setSteps(pipeline?.steps ?? []);
    console.log("Pipeline updated");
  }, [pipeline]);

  const { blueprints } = useBlueprintContext();
  const blueprintMap = useMemo(() => listToMap(blueprints, (bp: StepBlueprint) => bp.id), [blueprints]);

  const isSingleOperation = steps.length === 1 && pipeline.id.includes("single-operation");


  const onDragStart = () => setIsDragging(true);

  const onDragEnd = (result: DropResult) => {
    setIsDragging(false);
    if (!result.destination) return;

    const reorderedSteps = Array.from(steps);
    const [movedStep] = reorderedSteps.splice(result.source.index, 1);
    reorderedSteps.splice(result.destination.index, 0, movedStep);
    setSteps(reorderedSteps);
  };

  const handleSavePipeline = () => {
    onSavePipeline({
      ...pipeline,
      name: pipelineName,
      description: pipelineDescription,
      steps,
    });
    setShowSaved(true);
    setTimeout(() => setShowSaved(false), 2000);
  };

  const handleDeleteStep = (index: number) => () => {
    const updatedSteps = [...steps];
    updatedSteps.splice(index, 1);
    setSteps(updatedSteps);
    setSelectedStepIndex(null);
  }

  const handleAddOperationClick = () => {
    setShowOperationToolbox((prev) => !prev);
  };

  const handleOperationSelect = (blueprint: StepBlueprint) => {
    const newStep: StepValues = {
      stepId: blueprint.id,
      values: {},
      uniqueId: `unique-${Date.now()}`,
    };
    setSteps([...steps, newStep]);
    setShowOperationToolbox(false);
  };

  const handleClickOutside = (event: MouseEvent) => {
    if (
      toolboxRef.current &&
      !toolboxRef.current.contains(event.target as Node) &&
      addOperationRef.current &&
      !addOperationRef.current.contains(event.target as Node)
    ) {
      setShowOperationToolbox(false);
    }
  };

  useEffect(() => {
    if (showOperationToolbox) {
      document.addEventListener('mousedown', handleClickOutside);
    } else {
      document.removeEventListener('mousedown', handleClickOutside);
    }

    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [showOperationToolbox]);

  const toggleShowInput = () => {
    setShowInputCsv(!showInputCsv);
  }

  const csvData =
      inputHandle.type === 'csv' ? inputHandle.data : "text \n" + inputHandle.data;

  return (
    <div className="pipeline-config-screen">
      {/* Header */}
      <div className="pipeline-header">
        <h2>General Settings</h2>
        <label>Name:</label>
        <TextFieldPicker value={pipelineName} onChange={(name) => setPipelineName(name)} />
        <label>Description:</label>
        <TextFieldPicker value={pipelineDescription} onChange={(desc) => setPipelineDescription(desc)} />
      </div>

      {/* Operations */}
      <div className="operations-container">
        <h2>{isSingleOperation? "Configuration": "Operations"}</h2>
        <div className="pipeline-wrapper">
          {/* Input Box */}
          <div className="file-box input-box" onClick={toggleShowInput}>
            <FaFileAlt className="file-icon" />
            <span className="file-name">{inputHandle.name ?? "input"}</span>
          </div>

          <div className="arrow show">→</div>

          {/* Drag and Drop Context */}
          <DragDropContext onDragStart={onDragStart} onDragEnd={onDragEnd}>
            <Droppable droppableId="operations" direction="horizontal">
              {(provided) => (
                <div className="operations-section" ref={provided.innerRef} {...provided.droppableProps}>

                  {/* Draggable Operations */}
                  {steps.map((step, index) => {
                    const blueprint = blueprintMap[step.stepId];
                    const operationName = blueprint?.name ?? `Operation #${index + 1}`;
                    return (
                      <React.Fragment key={step.uniqueId}>
                        <Draggable draggableId={step.uniqueId} index={index}>
                          {(provided) => (
                            <div
                              className="draggable-operation"
                              ref={provided.innerRef}
                              {...provided.draggableProps}
                              {...provided.dragHandleProps}
                              onClick={() => setSelectedStepIndex(index === selectedStepIndex ? null : index)}
                            >
                              <OperationBox
                                operationName={operationName}
                                operationDescription={blueprint?.description ?? ''}
                                selected={selectedStepIndex === index}
                              />
                            </div>
                          )}
                        </Draggable>

                        {/* Arrow between operations */}
                        {!isDragging && !isSingleOperation && <div className="arrow show">→</div>}
                      </React.Fragment>
                    );
                  })}

                  {/* Add Operation Card */}
                  {!isDragging && !isSingleOperation && (
                    <div
                      className="add-operation-card"
                      onClick={handleAddOperationClick}
                      ref={addOperationRef}
                    >
                      +
                      {showOperationToolbox && (
                        <div className="operation-toolbox show" ref={toolboxRef}>
                          {blueprints.map((blueprint) => (
                            <div
                              key={blueprint.id}
                              className="toolbox-item"
                              onClick={() => handleOperationSelect(blueprint)}
                            >
                              <span className="operation-name">{blueprint.name}</span>
                              <span className="operation-description">{blueprint.description}</span>
                            </div>
                          ))}
                        </div>
                      )}
                    </div>
                  )}

                  {/* Arrow before Output Box */}


                  {provided.placeholder}
                </div>
              )}
            </Droppable>
          </DragDropContext>

          <div className="arrow show">→</div>

          {/* Output Box */}
          <div className="file-box output-box">
            <FaFileAlt className="file-icon" />
            <span className="file-name">{outputFileName}</span>
          </div>
        </div>
      </div>

      {/* Config Panel */}
      {selectedStepIndex !== null && (
        <div className="config-panel">
          <div className="operation-config-panel">
            <StepConfig
              blueprint={blueprintMap[steps[selectedStepIndex].stepId]}
              values={steps[selectedStepIndex]}
              onUpdate={(updatedValues) => {
                const updatedSteps = [...steps];
                updatedSteps[selectedStepIndex] = { ...updatedSteps[selectedStepIndex], ...updatedValues };
                setSteps(updatedSteps);
              }}
              onDeleteStep={handleDeleteStep(selectedStepIndex)}
              isSingleOperation={isSingleOperation}
            />
          </div>
        </div>
      )}

      {/* Buttons */}
      <div className="button-container">
        <button className="back-button" onClick={onPrevious}>
          <FaArrowLeft /> Back
        </button>
        <button className={`save-button ${showSaved ? 'show-saved' : ''}`} onClick={handleSavePipeline}>
          <FaSave /> Save
        </button>
        <button className="run-button" onClick={onNext}>
          <FaPlay /> Run Pipeline
        </button>
      </div>

      <OverlayWindow isOpen={showInputCsv} onClose={toggleShowInput} title="CSV Viewer">
        <CsvViewer rawData={csvData} maxRows={100} maxCellLength={300} />
      </OverlayWindow>

    </div>


  );
};

export default PipelineConfigScreen;
