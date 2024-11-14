// src/types/parameter.d.ts
import { PickerObject } from "./pickerObject";

export interface Parameter {
  name: string;
  type: string; // Basic type or 'complex' for complex types
  description: string;
  defaultValue: object | null
  picker?: PickerObject | null;
}
