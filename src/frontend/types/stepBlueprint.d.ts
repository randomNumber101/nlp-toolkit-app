// src/types/stepBlueprint.d.ts
import { InOutDef } from "./inOutDef";

export interface StepBlueprint {
  id: string;
  name: string;
  description: string;
  inOutDef: InOutDef;
}
