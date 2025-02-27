import * as React from 'react';
import { useState, useEffect } from 'react';
import { StepBlueprint, StepValues } from "../../types";
import "./StepConfig.scss";
import DynamicPicker from "../ValuePickers/DynamicPicker";
import {FaTrash} from "react-icons/fa";

interface StepConfigProps {
  blueprint: StepBlueprint;
  values: StepValues;
  onUpdate: (updatedValues: StepValues) => void;
  onDeleteStep: () => void;
  isSingleOperation?: boolean;
}

const StepConfigClass: React.FC<StepConfigProps> =
    ({ blueprint, values, onUpdate , onDeleteStep, isSingleOperation}) => {
  const [updatedValues, setUpdatedValues] = useState(values.values || {});
  const [isInfoExpanded, setIsInfoExpanded] = useState(false);
  const [isHovered, setIsHovered] = useState(false);

  useEffect(() => {
    setUpdatedValues(values.values || {});
  }, [values, blueprint]);

  const handleTempChange = (paramName: string, newValue: any) => {
    const newUpdatedValues = {
      ...updatedValues,
      [paramName]: newValue,
    };
    setUpdatedValues(newUpdatedValues);
    onUpdate({ ...values, values: newUpdatedValues });
  };

  console.log(blueprint)
  return (
    <div className="step-config">
      <div className="header">
        <div className="name">{blueprint.name}</div>
        {!isSingleOperation && (
          <button className="remove-step-button" onClick={onDeleteStep}>
              <FaTrash/>
          </button>
        )}
      </div>

      {blueprint.information && (
        <div className="info-border-container">
          <div className="description-container"
              onMouseEnter={() => setIsHovered(true)}
              onMouseLeave={() => setIsHovered(false)}
              onClick={() => setIsInfoExpanded(!isInfoExpanded)}
              aria-label="More information"
          >
            <div className={`description ${isHovered ? 'hovered' : ''}`}>
              <span className="arrow">{isInfoExpanded ? '▼' : '▶'}</span>
              {blueprint.description}
            </div>
            <button
              className="info-icon"
            >
              i
            </button>
          </div>

          <div className={`information-box ${isInfoExpanded ? 'expanded' : ''}`}
              dangerouslySetInnerHTML={{ __html: blueprint.information }} />
        </div>
      )}

      {!blueprint.information && blueprint.description && (
        <div className="description-container">
          <div className="description">
            {blueprint.description}
          </div>
        </div>
      )}

      <div className="static-parameters">
        {blueprint.inOutDef.staticParameters.map((parameter) => (
          <DynamicPicker
            key={parameter.name}
            parameter={parameter}
            value={updatedValues[parameter.name]}
            onChange={(newValue) => handleTempChange(parameter.name, newValue)}
          />
        ))}
      </div>
    </div>
  );
};

export default StepConfigClass;