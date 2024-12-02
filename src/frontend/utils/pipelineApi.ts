// src/utils/pipelineApi.ts

import { Pipeline, StepBlueprint, StepValues } from "../types";
import {VisualizationData} from "../types/events";

function unpackResponse(response: any) {
  if (response instanceof Error) {
    console.error(response.message);
    throw response;
  }
  return response;
}

async function waitForPywebview(): Promise<void> {
  console.log("Waiting for webview...")
  return new Promise((resolve, reject) => {
    const interval = setInterval(() => {
      if (typeof window.pywebview !== "undefined" && window.pywebview.api) {
        clearInterval(interval);
        clearTimeout(timeout);
        console.log("Webview is available. Exiting poll loop.");
        resolve();
      }
      else{
        console.log("Webview not available, yet");
      }
    }, 250);

    // Timeout after 3 seconds if pywebview is still unavailable
    const timeout = setTimeout(() => {
      clearInterval(interval);
      reject(new Error("pywebview API was not detected within 3 seconds"));
    }, 3000); // 3 seconds timeout
  });
}

// Load a single pipeline by its ID
export async function loadPipeline(pipelineId: string): Promise<Pipeline | null> {
  await waitForPywebview();
  try {
    const response = await window.pywebview.api.load_pipeline(pipelineId);
    const result = unpackResponse(response);
    return result as Pipeline; // Cast to Pipeline interface
  } catch (error) {
    console.error("Failed to load pipeline:", error);
    return null;
  }
}

// Save a pipeline configuration by its ID
export async function savePipeline(config: Pipeline): Promise<boolean> {
  await waitForPywebview();
  try {
    const response = await window.pywebview.api.STORAGE.save_pipeline(config);
    const result = unpackResponse(response);
    return result as boolean; // Cast result to boolean
  } catch (error) {
    console.error("Failed to save pipeline:", error);
    return false;
  }
}

// List all pipelines
export async function listPipelines(): Promise<Pipeline[]> {
  await waitForPywebview();
  try {
    const response = await window.pywebview.api.STORAGE.load_all_pipelines();
    console.log(response)
    const result = unpackResponse(response);
    return result as Pipeline[]; // Cast response to Pipeline array
  } catch (error) {
    console.error("Failed to list pipelines:", error);
    return [];
  }
}

// List all step blueprints
export async function listStepBlueprints(): Promise<StepBlueprint[]> {
  await waitForPywebview();

  const response = await window.pywebview.api.STORAGE.load_all_steps();
  console.log(response)
  const result = unpackResponse(response);
  return result as StepBlueprint[]; // Cast response to StepBlueprint array
}

// Load a specific step blueprint by its ID
export async function loadStepBlueprint(stepId: string): Promise<StepBlueprint | null> {
  await waitForPywebview();
  try {
    const response = await window.pywebview.api.STORAGE.load_step(stepId);
    const result = unpackResponse(response);
    console.log("Retrieved blueprint for " + stepId)
    console.log(result)
    return result as StepBlueprint; // Cast to StepBlueprint interface
  } catch (error) {
    console.error("Failed to load step blueprint:", error);
    return null;
  }
}

export async function invokeEvent(name, data): Promise<null> {
    await waitForPywebview();
  try {
    const response = await window.pywebview.api.RUNS.invokeEvent(name, data);
    return null// Cast to StepBlueprint interface
  } catch (error) {
    console.error("Failed to invoke event:", error);
    return null;
  }
}

// Starts a run in a seperate Thread and returns its callback (run_id : string)
export async function startRun(pipelineId, input): Promise<string> {
  await waitForPywebview()
  try {
    const response = await window.pywebview.api.RUNS.startRun(pipelineId, input);
    const result = unpackResponse(response)
    return result as string;
  } catch (error) {
    console.error("Failed to invoke event:", error);
    return null;
  }
}

export async function getRunVisualization(run_id : string, step_index: number): Promise<VisualizationData> {
  await waitForPywebview()
  try {
    const response = await window.pywebview.api.RUNS.getVisualization(run_id, step_index);
    const result = unpackResponse(response)
    return result as VisualizationData;
  } catch (error) {
    console.error("Failed to invoke event:", error);
    return null;
  }
}

export async function getRunResult(run_id : string, step_index: number): Promise<any> {
  await waitForPywebview()
  try {
    const response = await window.pywebview.api.RUNS.getResult(run_id);
    const result = unpackResponse(response)
    return result
  } catch (error) {
    console.error("Failed to invoke event:", error);
    return null;
  }
}
