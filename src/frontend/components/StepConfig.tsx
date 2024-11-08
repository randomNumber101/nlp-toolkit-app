// src/components/StepConfigClass.tsx

import * as React from 'react';
import { useState, useEffect } from 'react';
import { StepBlueprint, StepValues } from '../types'; // Define the blueprint for each step
import DynamicPicker from './valuePicker/DynamicPicker'; // Main dynamic picker component

interface StepConfigProps {
  blueprint: StepBlueprint; // Blueprint containing parameter definitions
  values: StepValues; // Existing values in the pipeline for this step
  onUpdate: (updatedValues: StepValues) => void; // Callback to update values
}

const StepConfigClass: React.FC<StepConfigProps> = ({ blueprint, values, onUpdate }) => {
  const [parameters, setParameters] = useState(values.values || {});

  // Update the local parameters when values or blueprint changes
  useEffect(() => {
    setParameters(values.values || {});
  }, [values, blueprint]);

  // Handler to update a single parameter value
  const handleParameterChange = (paramName: string, newValue: any) => {
    const updatedValues = {
      ...parameters,
      [paramName]: newValue,
    };
    setParameters(updatedValues);

    // Trigger callback to update parent component with new values
    onUpdate({ ...values, values: updatedValues });
  };

  return (
    <div className="step-config">
      <h3>{blueprint.name}</h3>
      <p>{blueprint.description}</p>

      {blueprint.inOutDef.staticParameters.map((parameter) => (
        <DynamicPicker
          key={parameter.name}
          parameter={parameter}
          value={parameters[parameter.name]}
          onChange={(newValue) => handleParameterChange(parameter.name, newValue)}
        />
      ))}
    </div>
  );
};

export default StepConfigClass;
