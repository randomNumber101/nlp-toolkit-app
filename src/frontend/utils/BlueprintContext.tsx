import * as React from 'react'

import { createContext, useState, useContext } from 'react';
import { StepBlueprint } from '../types';

interface BlueprintContextType {
  blueprints: StepBlueprint[];
  setBlueprints: React.Dispatch<React.SetStateAction<StepBlueprint[]>>;
}

export const BlueprintContext = createContext<BlueprintContextType | undefined>(undefined);

export const useBlueprintContext = () => {
  const context = useContext(BlueprintContext);
  if (!context) throw new Error('useBlueprintContext must be used within a BlueprintProvider');
  return context;
};
