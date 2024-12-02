import * as React from 'react';
import { useEffect, useState } from "react";
import LandingPage from './LandingPage/LandingPage';
import PipelineConfigScreen from './PipelineConfigScreen/PipelineConfigScreen';
import InputScreen from './InputScreen/InputScreen';
import RunScreen from './RunScreen/RunScreen';

import LoadingAnimation from "../components/LoadingScreen/Loading";
import {invokeEvent, listPipelines, loadStepBlueprint, savePipeline} from "../utils/pipelineApi";
import {streamToString} from "../utils/functional";
import { Pipeline, StepBlueprint } from '../types';
import {InputHandle} from './InputScreen/InputScreen'
import {useBackendEvent} from "../utils/useBackendEvents";


function App() {
  const [currentScreen, setCurrentScreen] = useState('loading');
  const [selectedPipeline, setSelectedPipeline] = useState<Pipeline | null>(null);
  const [inputHandle, setInput] = useState<InputHandle | null>(null)

  const [pipelines, setPipelines] = useState<Pipeline[]>([
    { id: "sentiment", name: 'Dummy Pipe (should not show)', description: 'Analyze the sentiment of text data' , steps: []},] );
  const [blueprintMap, setBlueprintMap] = useState<{ [key: string]: StepBlueprint }>({});

  console.log("App started.")

  useBackendEvent("test", (event) => {
      console.log(event)
    });

  useEffect(() => {
    invokeEvent("test", {
      "status" : "succeeded",
      "data" : {"number" : 420}
    }).then(_ => console.log("Sent event."))
  }, [])

  async function loadBlueprints(pipeline: Pipeline) {
    const _current_screen = currentScreen
    setCurrentScreen('loading')
    if (pipeline != null) {
      // Only update blueprint map if selectedPipeline is not null
      const loadedBlueprints = await Promise.all(pipeline.steps.map(s => loadStepBlueprint(s.stepId)));
      const bpMap = {} as { [key: string]: StepBlueprint };
      loadedBlueprints.forEach(bp => {
        bpMap[bp.id] = bp
      })
      setBlueprintMap(bpMap);
      console.log("Set blueprint map to something.");
    } else {
      setBlueprintMap({});
      console.log("Pipeline is null.");
    }
    setCurrentScreen(_current_screen)
  }

  async function loadPipelines() {
    const _current_screen = currentScreen
    setCurrentScreen('loading')
    const pipelines = await listPipelines();
    console.log(pipelines[0])
    setPipelines(pipelines);
    setCurrentScreen(_current_screen)
  }

  useEffect(() => {
    if (!inputHandle)
      goToInputScreen()
  }, [inputHandle])

  const goToLandingPage = () => {
    loadPipelines().then(() => setCurrentScreen('landing'));
  };

  const goToConfigScreen = (pipeline: Pipeline) => {
    console.log("Retrieved pipeline:");
    console.log(pipeline);
    setSelectedPipeline(pipeline); // This will trigger useEffect to run updateBlueprintMap
    loadBlueprints(pipeline).then(_ => setCurrentScreen('pipelineConfig'))
  };

  const goToInputScreen = () => {
    setCurrentScreen('input');
  };

  const goToResultsScreen = (pipeline: Pipeline) => {
    setSelectedPipeline(pipeline)
    loadBlueprints(pipeline).then(_ => setCurrentScreen('results'))
  };

  const onSavePipeline = (pipeline: Pipeline) => {
    savePipeline(pipeline).catch(console.log);
    const index = pipelines.findIndex(p => p.id == pipeline.id)
    const newPipelines = {...pipelines}
    newPipelines[index] = {...pipeline}
    setSelectedPipeline(pipeline)
    setPipelines(newPipelines)
  };

  const handleInput = (input: InputHandle) => {
    setInput(input)
    console.log(input.name)
    goToLandingPage()
  }

  const renderScreen = () => {
    switch (currentScreen) {
      case 'loading': {
        return <LoadingAnimation message={"Loading configurations..."}/>
      }
      case 'landing':
        return (
          <LandingPage
            pipelines={pipelines}
            onAddPipeline={() => setCurrentScreen('pipelineConfig')}
            onSelectPipeline={goToConfigScreen}
            onRunPipeline={goToResultsScreen}
          />
        );
      case 'pipelineConfig':
        console.log("Going to Config Screen. Pipeline is: ", selectedPipeline)
        return <PipelineConfigScreen
          initialPipe={selectedPipeline}
          blueprintMap={blueprintMap}
          onPrevious={goToLandingPage}
          onNext={goToInputScreen}
          onSavePipeline={onSavePipeline}
        />;
      case 'input':
        return <InputScreen onGoToPipelineScreen={handleInput} />;
      case 'results':
        return <RunScreen
            pipeline={selectedPipeline}
            inputHandle={inputHandle}
            blueprints={blueprintMap}
        />;
      default:
        return (
          <LandingPage
            pipelines={pipelines}
            onAddPipeline={() => setCurrentScreen('pipelineConfig')}
            onSelectPipeline={goToConfigScreen}
            onRunPipeline={goToInputScreen}
          />
        );
    }
  };

  return <div>{renderScreen()}</div>;
}

export default App;
