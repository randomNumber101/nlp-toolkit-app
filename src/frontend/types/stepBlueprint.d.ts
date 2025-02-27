// src/types/stepBlueprint.d.ts
import { InOutDef } from "./inOutDef";

export interface StepBlueprint {
  id: string;
  name: string;
  description: string;
  information: string;
  inOutDef: InOutDef;
  tags: string[];
}
