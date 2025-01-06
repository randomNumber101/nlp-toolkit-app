// src/types/pipeline.d.ts
import { StepValues } from "./stepValues";

export interface Pipeline {
  id: string; // Using string because UUIDs are typically represented as strings
  name: string;
  description: string;
  steps: StepValues[];
  tags: string[];
}
