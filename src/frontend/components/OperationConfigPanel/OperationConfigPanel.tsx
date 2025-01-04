import * as React from 'react'
// src/components/OperationConfigPanel/OperationConfigPanel.tsx

import { StepBlueprint, StepValues } from '../../types';
import StepConfig from '../StepConfig/StepConfig';
import './OperationConfigPanel.scss';

interface OperationConfigPanelProps {
  operationName: string;
  blueprint: StepBlueprint;
  values: StepValues;
  onUpdate: (newValues: StepValues) => void;
}

const OperationConfigPanel: React.FC<OperationConfigPanelProps> = ({
  operationName,
  blueprint,
  values,
  onUpdate,
}) => {
  return (
    <div className="operation-config-panel">
      <StepConfig
        blueprint={blueprint}
        values={values}
        onUpdate={onUpdate}
      />
    </div>
  );
};

export default OperationConfigPanel;

