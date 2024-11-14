import * as React from 'react';
import { useEffect, useState } from "react";
import LandingPage from './LandingPage/LandingPage';
import PipelineConfigScreen from './PipelineConfigScreen/PipelineConfigScreen';
import InputScreen from './InputScreen/InputScreen';
import ResultsScreen from './ResultScreen/ResultScreen';
import { Pipeline, StepBlueprint } from '../types';
import { loadStepBlueprint, savePipeline } from "../utils/pipelineApi";

function App() {
  const [currentScreen, setCurrentScreen] = useState('landing');
  const [selectedPipeline, setSelectedPipeline] = useState<Pipeline | null>(null);
  const [blueprintMap, setBlueprintMap] = useState<{ [key: string]: StepBlueprint }>({});
  const [loadingConfig, setLoading] = useState(false)

  async function loadBlueprints(pipeline: Pipeline) {
    if (pipeline != null) {
      setLoading(true)
      // Only update blueprint map if selectedPipeline is not null
      const loadedBlueprints = await Promise.all(pipeline.steps.map(s => loadStepBlueprint(s.stepId)));
      const bpMap = {} as { [key: string]: StepBlueprint };
      loadedBlueprints.forEach(bp => {
        bpMap[bp.id] = bp
      })
      setBlueprintMap(bpMap);
      console.log("Set blueprint map to something.");
      setLoading(false)
    } else {
      setBlueprintMap({});
      console.log("Pipeline is null.");
    }
  }

  const goToLandingPage = () => {
    setCurrentScreen('landing');
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
      case 'landing':
        return (
          <LandingPage
            onAddPipeline={() => setCurrentScreen('pipelineConfig')}
            onSelectPipeline={goToConfigScreen}
            onRunPipeline={goToInputScreen}
          />
        );
      case 'pipelineConfig':
        console.log("Going to Config Screen. Blueprints are: ", blueprintMap)
        if (loadingConfig) {
          return <div>Loading pipeline...</div>
        }
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
