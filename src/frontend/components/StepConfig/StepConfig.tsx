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
}

const StepConfigClass: React.FC<StepConfigProps> = ({ blueprint, values, onUpdate , onDeleteStep}) => {
  const [updatedValues, setUpdatedValues] = useState(values.values || {});

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

  return (
    <div className="step-config">
      <div className="header">
        <div className="name">{blueprint.name}</div>
        <button className="remove-step-button" onClick={onDeleteStep}>
            <FaTrash/>
        </button>
      </div>
      <div className="description">{blueprint.description}</div>

      <div className="static-parameters">
        {/* Render DynamicPicker with updatedValues */}
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
