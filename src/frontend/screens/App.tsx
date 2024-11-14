import * as React from 'react';
import { useEffect, useState } from "react";
import LandingPage from './LandingPage/LandingPage';
import PipelineConfigScreen from './PipelineConfigScreen/PipelineConfigScreen';
import InputScreen from './InputScreen/InputScreen';
import ResultsScreen from './ResultScreen/ResultScreen';
import { Pipeline, StepBlueprint } from '../types';
import {listPipelines, loadStepBlueprint, savePipeline} from "../utils/pipelineApi";
import LoadingAnimation from "../components/LoadingScreen/Loading";


function App() {
  const [currentScreen, setCurrentScreen] = useState('loading');
  const [selectedPipeline, setSelectedPipeline] = useState<Pipeline | null>(null);

  const [pipelines, setPipelines] = useState<Pipeline[]>([
    { id: "sentiment", name: 'Dummy Pipe (should not show)', description: 'Analyze the sentiment of text data' , steps: []},] );
  const [blueprintMap, setBlueprintMap] = useState<{ [key: string]: StepBlueprint }>({});


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
    goToLandingPage()
  }, [])

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

  const goToResultsScreen = () => {
    setCurrentScreen('results');
  };

  const onSavePipeline = (pipeline: Pipeline) => {
    savePipeline(pipeline).catch(console.log);
    setSelectedPipeline(pipeline);
    setCurrentScreen('landing');
  };

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
            onRunPipeline={goToInputScreen}
          />
        );
      case 'pipelineConfig':
        console.log("Going to Config Screen. Blueprints are: ", blueprintMap)
        return <PipelineConfigScreen
          pipeline={selectedPipeline}
          blueprintMap={blueprintMap}
          onPrevious={goToLandingPage}
          onNext={goToInputScreen}
          onSavePipeline={onSavePipeline}
        />;
      case 'input':
        return <InputScreen onNext={goToResultsScreen} />;
      case 'results':
        return <ResultsScreen pipeline={selectedPipeline} />;
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
