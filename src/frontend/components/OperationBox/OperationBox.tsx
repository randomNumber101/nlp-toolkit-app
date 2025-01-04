import * as React from 'react';
import './OperationBox.scss';

interface OperationBoxProps {
  operationName: string;
  operationDescription: string;
}

const OperationBox: React.FC<OperationBoxProps> = ({ operationName, operationDescription }) => {
  return (
    <div className="operation-box" title={operationDescription}>
      {operationName}
    </div>
  );
};

export default OperationBox;
