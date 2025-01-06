import * as React from 'react';
import { useState, useEffect } from 'react';
import { StepBlueprint, StepValues } from "../../types";
import "./StepConfig.scss";
import DynamicPicker from "../ValuePickers/DynamicPicker";

interface StepConfigProps {
  blueprint: StepBlueprint;
  values: StepValues;
  onUpdate: (updatedValues: StepValues) => void;
}

const StepConfigClass: React.FC<StepConfigProps> = ({ blueprint, values, onUpdate }) => {
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
      <div className="name">{blueprint.name}</div>
      <div className="description">{blueprint.description}</div>

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
  );
};

export default StepConfigClass;
