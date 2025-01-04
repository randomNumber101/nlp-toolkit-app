import React from 'react';
import './OperationBox.scss';

interface OperationBoxProps {
  operationName: string;
  operationDescription: string;
  selected: boolean;
}

const OperationBox: React.FC<OperationBoxProps> = ({
  operationName,
  operationDescription,
  selected,
}) => {
  return (
    <div className={`operation-box ${selected ? 'selected' : ''}`} title={operationDescription}>
      {operationName}
    </div>
  );
};

export default OperationBox;
