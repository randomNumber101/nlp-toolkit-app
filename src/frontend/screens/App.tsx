import * as React from 'react';
import {useState} from "react";
import LandingPage from './LandingPage/LandingPage';
import PipelineConfigScreen from './PipelineConfigScreen/PipelineConfigScreen';
import InputScreen from './InputScreen/InputScreen';
import ResultsScreen from './ResultScreen/ResultScreen';
import {Pipeline} from '../types'
import {savePipeline} from "../utils/pipelineApi";

function App() {
  const [currentScreen, setCurrentScreen] = useState('landing');
  const [selectedPipeline, setSelectedPipeline] = useState<Pipeline | null>(null);

  const goToLandingPage = () => {
    setCurrentScreen('landing')
  }

  const goToConfigScreen = (pipeline : Pipeline) => {
    setSelectedPipeline(pipeline);
    setCurrentScreen('pipelineConfig');
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
  }

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
        return <PipelineConfigScreen
            pipeline={selectedPipeline}
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