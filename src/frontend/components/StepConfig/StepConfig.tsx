// src/components/StepConfigClass.tsx

import * as React from 'react';
import { useState, useEffect } from 'react';
import {StepBlueprint, StepValues} from "../../types";
import DynamicPicker from "../ValuePickers/DynamicPicker";

interface StepConfigProps {
  blueprint: StepBlueprint;
  values: StepValues;
  onUpdate: (updatedValues: StepValues) => void;
}

const StepConfigClass: React.FC<StepConfigProps> = ({ blueprint, values, onUpdate }) => {
  const [updatedValues, setUpdatedValues] = useState(values.values || {});

  useEffect(() => {
    console.log("Values changed: ", updatedValues)
    onUpdate({ ...values, values: updatedValues });
  }, [updatedValues]);

  useEffect(() => {
    setUpdatedValues(values.values || {});
  }, [values, blueprint]);

  const handleTempChange = (paramName: string, newValue: any) => {
    setUpdatedValues((prevValues) => ({
      ...prevValues,
      [paramName]: newValue,
    }));
  };

  return (
    <div className="step-config">
      <h3>{blueprint.name}</h3>
      <p>{blueprint.description}</p>

      {/* Render DynamicPicker with updatedValues */}
      {blueprint.inOutDef.staticParameters.map((parameter) => (
        <DynamicPicker
          key={parameter.name}
          parameter={parameter}
          value={updatedValues[parameter.name]} // Use updatedValues here
          onChange={(newValue) => handleTempChange(parameter.name, newValue)}
        />
      ))}

    </div>
  );
};

export default StepConfigClass;
