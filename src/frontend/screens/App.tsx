import * as React from 'react';
import {useState} from "react";
import LandingPage from './LandingPage/LandingPage';
import PipelineConfigScreen from './PipelineConfigScreen/PipelineConfigScreen';
import InputScreen from './InputScreen/InputScreen';
import ResultsScreen from './ResultScreen/ResultScreen';
import {Pipeline} from '../types'

function App() {
  const [currentScreen, setCurrentScreen] = useState('landing');
  const [selectedPipeline, setSelectedPipeline] = useState<Pipeline | null>(null);

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
            onNext={goToInputScreen}
            onSavePipeline={(updatedPipeline) => setSelectedPipeline(updatedPipeline)}
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