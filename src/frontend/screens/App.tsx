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
import { invokeEvent, listPipelines, loadStepBlueprint, savePipeline } from "../utils/pipelineApi";
import { Pipeline, StepBlueprint } from '../types';
import { InputHandle } from './InputScreen/InputScreen';
import { useBackendEvent } from "../utils/useBackendEvents";

type Screen =
  | 'loading'
  | 'input'
  | 'landing'
  | 'pipelineConfig'
  | 'results';

const steps = [
  'Select Input',
  'Select Pipeline',
  'Configure Pipeline',
  'Run Pipeline',
];

function App() {
  const [currentScreen, setCurrentScreen] = useState<Screen>('loading');
  const [currentStep, setCurrentStep] = useState<number>(0);
  const [selectedPipeline, setSelectedPipeline] = useState<Pipeline | null>(null);
  const [inputHandle, setInput] = useState<InputHandle | null>(null);

  const [pipelines, setPipelines] = useState<Pipeline[]>([]);
  const [blueprintMap, setBlueprintMap] = useState<{ [key: string]: StepBlueprint }>({});

  useBackendEvent("test", (event) => {
    console.log(event);
  });

  useEffect(() => {
    invokeEvent("test", {
      status: "succeeded",
      data: { number: 420 },
    }).then(() => console.log("Sent event."));
  }, []);

  async function loadBlueprints(pipeline: Pipeline) {
    const _current_screen = currentScreen;
    setCurrentScreen('loading');
    if (pipeline != null) {
      console.log("Loading blueprints..")
      // Only update blueprint map if selectedPipeline is not null
      const loadedBlueprints = await Promise.all(pipeline.steps.map(s => loadStepBlueprint(s.stepId)));
      const bpMap = {} as { [key: string]: StepBlueprint };
      loadedBlueprints.forEach(bp => {
        bpMap[bp.id] = bp;
      });
      setBlueprintMap(bpMap);
    } else {
      console.error("Blueprint Map is null as pipeline is: ", pipeline)
      setBlueprintMap({});
    }
    setCurrentScreen(_current_screen);
  }

  async function loadPipelines() {
    const _current_screen = currentScreen;
    setCurrentScreen('loading');
    const pipelines = await listPipelines();
    setPipelines(pipelines);
    setCurrentScreen(_current_screen);
  }

  useEffect(() => {
    if (currentScreen === 'loading') {
      // Initial load
      goToInputScreen();
    }
  }, []);

  const goToLandingPage = () => {
    loadPipelines().then(() => {
      setCurrentScreen('landing');
      setCurrentStep(1);
    });
  };

  const goToConfigScreen = (pipeline: Pipeline) => {
    setSelectedPipeline(pipeline);
    loadBlueprints(pipeline).then(() => {
      setCurrentScreen('pipelineConfig');
      setCurrentStep(2);
    });
  };

  const goToInputScreen = () => {
    setCurrentScreen('input');
    setCurrentStep(0);
  };

  const goToResultsScreen = (pipeline: Pipeline) => {
    setSelectedPipeline(pipeline);
    loadBlueprints(pipeline).then(() => {
      setCurrentScreen('results');
      setCurrentStep(3);
    });
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
            pipelines={pipelines}
            onAddPipeline={() => setCurrentScreen('pipelineConfig')}
            onSelectPipeline={goToConfigScreen}
            onRunPipeline={goToResultsScreen}
          />
        );
      case 'pipelineConfig':
        return (
          <PipelineConfigScreen
            initialPipe={selectedPipeline}
            blueprintMap={blueprintMap}
            onPrevious={goToLandingPage}
            onNext={() => {
              if (selectedPipeline) {
                goToResultsScreen(selectedPipeline);
              }
            }}
            onSavePipeline={onSavePipeline}
          />
        );
      case 'results':
        if (selectedPipeline && inputHandle) {
          return (
            <RunScreen
              pipeline={selectedPipeline}
              inputHandle={inputHandle}
              blueprints={blueprintMap}
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
      <div className="app-content">
        {renderScreen()}
      </div>
    </div>
  );
}

export default App;
