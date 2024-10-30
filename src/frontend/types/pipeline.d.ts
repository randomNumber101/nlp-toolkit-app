// src/types/pipeline.d.ts

import {Step} from "./step";

export interface Pipeline {
  id: number;
  name: string;
  description: string;
  steps: Step[]; 
}
