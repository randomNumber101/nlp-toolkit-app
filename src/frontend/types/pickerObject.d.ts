// src/types/pickerObject.d.ts
import { Parameter } from "./parameter";

export interface PickerObject {
  name: string;
  outputType: string;
  parameters?: Parameter[]; // Optional for complex types
  values?: { [key: string]: any }; // Dictionary for non-complex types
}
