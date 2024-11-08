// src/types/inOutDef.d.ts
import { Parameter } from "./parameter";

export interface InOutDef {
  staticParameters: Parameter[];
  dynamicParameters: Parameter[];
  outputParameters: Parameter[];
}
