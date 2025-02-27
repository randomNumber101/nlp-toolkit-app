// src/components/App.tsx

import * as React from 'react';
import { useEffect, useState } from 'react';
import './App.scss';

import LandingPage from './LandingPage/LandingPage';
import PipelineConfigScreen from './PipelineConfigScreen/PipelineConfigScreen';
import InputScreen from './InputScreen/InputScreen';
import RunScreen from './RunScreen/RunScreen';
import StepperHeader from '../components/StepperHeader/StepperHeader';
import LoadingAnimation from "../components/LoadingScreen/Loading";
import {invokeEvent, listPipelines, listStepBlueprints, loadStepBlueprint, savePipeline} from "../utils/pipelineApi";
import { Pipeline, StepBlueprint } from '../types';
import { InputHandle } from './InputScreen/InputScreen';
import { useBackendEvent } from "../utils/useBackendEvents";
import {BlueprintContext, BlueprintProvider} from "../utils/BlueprintContext";
import {PipelineContext} from "../utils/PipelineContext";
import {InputHandleContext} from "../utils/InputHandleContext";

type Screen =
  | 'loading'
  | 'input'
  | 'landing'
  | 'pipelineConfig'
  | 'results';

const steps = [
  'Select Input',
  'Select Operation',
  'Configure Operation',
  'Run Operation',
];

function App() {
  const [currentScreen, setCurrentScreen] = useState<Screen>('loading');
  const [currentStep, setCurrentStep] = useState<number>(0);
  const [selectedPipeline, setSelectedPipeline] = useState<Pipeline | null>(null);

  const [inputHandle, setInput] = useState<InputHandle | null>(null);
  const [pipelines, setPipelines] = useState<Pipeline[]>([]);
  const [blueprints, setBlueprints] = useState<StepBlueprint[]>([])

  function getBlueprintMap() {
    const bpMap = {} as { [key: string]: StepBlueprint };
    blueprints.forEach(bp => {
      bpMap[bp.id] = bp;
    });
    return bpMap
  }


  async function loadConfigurations() {
    const _current_screen = currentScreen;

    // Only set the loading screen if configuration is needed
    if (_current_screen !== "input")
      setCurrentScreen('loading');

    // Load pipelines
    const pipelines = await listPipelines();
    setPipelines(pipelines);

    // Load Operation Blueprints
    const loadedBlueprints = await listStepBlueprints()
    setBlueprints(loadedBlueprints)

    setCurrentScreen(_current_screen);
  }

  useEffect(() => {
    if (currentScreen === 'loading') {
      // Initial load
      loadConfigurations().then(() => goToInputScreen())
    }
  }, []);

  const goToLandingPage = () => {
    setCurrentScreen('landing');
    setCurrentStep(1);
  };

  const goToConfigScreen = (pipeline: Pipeline) => {
    setSelectedPipeline(pipeline);
    setCurrentScreen('pipelineConfig');
    setCurrentStep(2);
  };

  const goToInputScreen = () => {
    setCurrentScreen('input');
    setCurrentStep(0);
  };

  const goToResultsScreen = (pipeline: Pipeline) => {
    setSelectedPipeline(pipeline);
    setCurrentScreen('results');
    setCurrentStep(3);
  };

  const onSavePipeline = (pipeline: Pipeline) => {
    savePipeline(pipeline).catch(console.log);
    const index = pipelines.findIndex(p => p.id === pipeline.id);
    const newPipelines = [...pipelines];
    if (index !== -1) {
      newPipelines[index] = { ...pipeline };
    } else {
      newPipelines.push(pipeline);
    }
    setSelectedPipeline(pipeline);
    setPipelines(newPipelines);
  };

  const onAddPipeline = () => {
    const newPipeline = {
      id: `pipeline-${Date.now()}`,
      name: 'New Pipeline',
      description: 'No description',
      steps: [],
      tags: [],
    } as Pipeline;

    savePipeline(newPipeline).catch(console.log);
    setPipelines([...pipelines, newPipeline]);
    setSelectedPipeline(newPipeline);
    setCurrentScreen('pipelineConfig')
  }

  const handleInput = (input: InputHandle) => {
    setInput(input);
    goToLandingPage();
  };

  const handleStepClick = (stepIndex: number) => {
    if (stepIndex <= currentStep) {
      switch (stepIndex) {
        case 0:
          goToInputScreen();
          break;
        case 1:
          goToLandingPage();
          break;
        case 2:
          if (selectedPipeline) {
            goToConfigScreen(selectedPipeline);
          } else {
            goToLandingPage();
          }
          break;
        case 3:
          if (selectedPipeline && inputHandle) {
            goToResultsScreen(selectedPipeline);
          }
          break;
        default:
          break;
      }
    }
  };

  const renderScreen = () => {
    switch (currentScreen) {
      case 'loading':
        return <LoadingAnimation message={"Loading configurations..."} />;
      case 'input':
        return <InputScreen preloaded={inputHandle} onGoToPipelineScreen={handleInput} />;
      case 'landing':
        return (
          <LandingPage
            onAddPipeline={onAddPipeline}
            onSelectPipeline={goToConfigScreen}
            onRunPipeline={goToResultsScreen}
          />
        );
      case 'pipelineConfig':
        return (
          <PipelineConfigScreen
            initialPipe={selectedPipeline}
            onPrevious={goToLandingPage}
            onNext={() => {
              if (selectedPipeline) {
                goToResultsScreen(selectedPipeline);
              }
            }}
            onSavePipeline={onSavePipeline}
            outputFileName={"output"}
          />
        );
      case 'results':
        if (selectedPipeline && inputHandle) {
          return (
            <RunScreen
              pipeline={selectedPipeline}
            />
          );
        } else {
          return <LoadingAnimation message={"Preparing to run pipeline..."} />;
        }
      default:
        return <LoadingAnimation message={"Loading..."} />;
    }
  };


  return (
    <div className="app-container">
      <StepperHeader steps={steps} currentStep={currentStep} onStepClick={handleStepClick} />
      <PipelineContext.Provider value={{pipelines, setPipelines}}>
        <BlueprintContext.Provider value={{blueprints, setBlueprints}}>
          <InputHandleContext.Provider value={inputHandle}>
            <div className="app-content">
              {renderScreen()}
            </div>
          </InputHandleContext.Provider>
        </BlueprintContext.Provider>
      </PipelineContext.Provider>
    </div>
  );
}

export default App;
