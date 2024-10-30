// src/types/step.d.ts

export interface Step {
  id: number;
  name: string;
  description: string;
  parameters: Record<string, any>;
}
