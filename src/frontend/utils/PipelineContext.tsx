import * as React from 'react'

import { createContext, useState, useContext } from 'react';
import { Pipeline } from '../types';

interface PipelineContextType {
  pipelines: Pipeline[];
  setPipelines: React.Dispatch<React.SetStateAction<Pipeline[]>>;
}

export const PipelineContext = createContext<PipelineContextType | undefined>(undefined);


export const usePipelineContext = () => {
  const context = useContext(PipelineContext);
  if (!context) throw new Error('usePipelineContext must be used within a PipelineProvider');
  return context;
};
