import React, { useState } from 'react';
import LandingPage from './components/screens/LandingPage/LandingPage';
import PipelineConfigScreen from './components/screens/PipelineConfigScreen/PipelineConfigScreen';
import InputScreen from './components/screens/InputScreen/InputScreen';
import ResultsScreen from './components/screens/ResultScreen/ResultScreen';

function App() {
  const [currentScreen, setCurrentScreen] = useState('landing');
  const [selectedPipeline, setSelectedPipeline] = useState(null);

  const goToConfigScreen = (pipeline) => {
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
        return <PipelineConfigScreen pipeline={selectedPipeline} onNext={goToInputScreen} />;
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