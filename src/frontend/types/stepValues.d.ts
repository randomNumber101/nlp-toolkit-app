// src/types/stepValues.d.ts
import { StepBlueprint } from "./stepBlueprint";

export interface StepValues {
  stepId: string;
  values: { [key: string]: any }; // Assuming values are JSON-serializable objects
}
