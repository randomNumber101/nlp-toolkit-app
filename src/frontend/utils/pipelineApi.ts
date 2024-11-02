// src/utils/pipelineApi.ts

import {Pipeline} from "../types";

async function waitForPywebview(): Promise<void> {
  return new Promise((resolve, reject) => {
    const interval = setInterval(() => {
      if (typeof window.pywebview !== 'undefined' && window.pywebview.api) {
        clearInterval(interval);
        clearTimeout(timeout);
        console.log("Webview is available. Exiting poll loop.")
        resolve();
      }
      console.log("Webview not available, yet");
    }, 250);

    // Timeout after 3 seconds if pywebview is still unavailable
    const timeout = setTimeout(() => {
      clearInterval(interval);
      reject(new Error("pywebview API was not detected within 3 seconds"));
    }, 3000); // 3 seconds timeout
  });
}

// Load a single pipeline by its ID
export async function loadPipeline(pipelineId: number): Promise<Pipeline | null> {
  await waitForPywebview();
  try {
    const response = await window.pywebview.api.load_pipeline(pipelineId);
    if (response.status === 'success') {
      return response.data as Pipeline;
    } else {
      console.error(response.message);
      return null;
    }
  } catch (error) {
    console.error("Failed to load pipeline:", error);
    return null;
  }
}

// Save a pipeline configuration by its ID
export async function savePipeline(config: Pipeline): Promise<boolean> {
  await waitForPywebview();
  try {
    const response = await window.pywebview.api.save_pipeline(config);
    if (response.status === 'success') {
      console.log(response.message);
      return true;
    } else {
      console.error(response.message);
      return false;
    }
  } catch (error) {
    console.error("Failed to save pipeline:", error);
    return false;
  }
}

// List all pipeline IDs
export async function listPipelines(): Promise<Pipeline[]> {
  await waitForPywebview();
  try {
    const response = await window.pywebview.api.list_pipelines();
    if (response.status === 'success') {
      return response.data.map(res => res.data);
    } else {
      console.error(response.message);
      return [];
    }
  } catch (error) {
    console.error("Failed to list pipelines:", error);
    return [];
  }
}
