import * as React from 'react'

import { createContext, useState, useContext } from 'react';
import {InputHandle} from "../screens/InputScreen/InputScreen";

export const InputHandleContext = createContext<InputHandle | null>(null);

export const useInputHandleContext = () => {
  const context = useContext(InputHandleContext);
  if (!context) throw new Error('useInputHandleContext must be used within a BlueprintProvider');
  return context;
};
