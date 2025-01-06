// src/components/LandingPage/LandingPage.tsx

import * as React from 'react';
import { useEffect, useState } from 'react';
import './LandingPage.scss';
import { Pipeline, StepBlueprint } from '../../types';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faCog, faPlay } from '@fortawesome/free-solid-svg-icons';
import { usePipelineContext } from '../../utils/PipelineContext';
import { useBlueprintContext } from '../../utils/BlueprintContext';
import { listToMap } from "../../utils/functional";

interface LandingPageProps {
  onAddPipeline: () => void;
  onSelectPipeline: (pipeline: Pipeline) => void;
  onRunPipeline: (pipeline: Pipeline) => void;
}

const LandingPage: React.FC<LandingPageProps> = ({
  onAddPipeline,
  onSelectPipeline,
  onRunPipeline,
}) => {
  const { pipelines, setPipelines } = usePipelineContext();
  const { blueprints } = useBlueprintContext();
  const [selectedTags, setSelectedTags] = useState<string[]>([]);

  // Create a map for quick blueprint lookup
  const blueprintMap = React.useMemo(() => listToMap(blueprints, (bp: StepBlueprint) => bp.id), [blueprints]);

  // Function to get all tags of a pipeline by aggregating tags from its steps
  const getPipelineTags = (pipeline: Pipeline): string[] => {
    const tagsSet = new Set<string>();
    pipeline.tags?.forEach(tag => tagsSet.add(tag));
    pipeline.steps.forEach(step => {
      const blueprint = blueprintMap[step.stepId];
      if (blueprint && blueprint.tags) {
        blueprint.tags.forEach(tag => tagsSet.add(tag));
      }
    });
    return Array.from(tagsSet);
  };

  // Collect all unique tags from blueprints
  const allTags = React.useMemo(() => {
    const tagSet = new Set<string>();

    pipelines.forEach(pipeline => {
      getPipelineTags(pipeline).forEach(tag => tagSet.add(tag));
    })

    return Array.from(tagSet).sort();
  }, [blueprints, pipelines, setPipelines]);

  // Effect to add operation pipelines based on blueprints
  useEffect(() => {
    // 1. Add Operation Pipelines
    const operationPipelines = blueprints.map((blueprint) => {
      const operationPipelineId = `${blueprint.id}-single-operation`;
      if (!pipelines.find((pipeline) => pipeline.id === operationPipelineId)) {
        return {
          id: operationPipelineId,
          name: blueprint.name,
          description: blueprint.description,
          steps: [{ stepId: blueprint.id, uniqueId: `unique-${Date.now()}` }],
          tags: ["operations"] // Assign "operations" tag
        } as Pipeline;
      }
      return null;
    }).filter((pipeline) => pipeline !== null) as Pipeline[];

    // 2. Add "pipelines" Tag to Non-Operation Pipelines
    const updatedPipelines = pipelines.map((pipeline) => {
      // Check if the pipeline is NOT a single operation pipeline
      const isOperationPipeline = String(pipeline.id).endsWith('-single-operation');

      // If it's not an operation pipeline and doesn't already have the "pipelines" tag, add it
      if (!isOperationPipeline && (!pipeline.tags || pipeline.tags.indexOf('pipelines') == -1)) {
        return {
          ...pipeline,
          tags: pipeline.tags ? [...pipeline.tags, 'pipelines'] : ['pipelines']
        };
      }

      return pipeline;
    });

    // 3. Update Pipelines State
    setPipelines(updatedPipelines);

    // 4. Add Operation Pipelines to State if Any
    if (operationPipelines.length > 0) {
      setPipelines((prev) => [...prev, ...operationPipelines]);
    }
  }, [blueprints, pipelines, setPipelines]);


  // Handler for adding a new pipeline
  const handleAddPipeline = () => {
    onAddPipeline();
  };

  // Handler for selecting a pipeline for configuration
  const handleSelectPipeline = (pipeline: Pipeline) => {
    onSelectPipeline(pipeline);
  };

  // Handler for running a pipeline
  const handleRunPipeline = (pipeline: Pipeline) => {
    onRunPipeline(pipeline);
  };

  // Handler for toggling tag selection
  const toggleTag = (tag: string) => {
    setSelectedTags((prev) =>
      prev.indexOf(tag) !== -1 ? prev.filter(t => t !== tag) : [...prev, tag]
    );
  };



  // Filter pipelines based on selected tags
  const filteredPipelines = React.useMemo(() => {
    if (selectedTags.length === 0) return pipelines;
    return pipelines.filter(pipeline => {
      const pipelineTags = getPipelineTags(pipeline);
      return selectedTags.every(tag => pipelineTags.indexOf(tag) !== -1);
    });
  }, [pipelines, selectedTags, blueprintMap]);

  // Render a single pipeline card
  const pipelineCard = (pipeline: Pipeline) => (
    <div
      key={pipeline.id}
      className={`pipeline-card ${typeof pipeline.id === 'string' && pipeline.id.endsWith('-single-operation') ? 'operation-card' : ''}`}
    >
      <div className="card-content">
        <h3 className="pipeline-title">{pipeline.name}</h3>
        <div className="description">
          <p>{pipeline.description}</p>
        </div>
      </div>
      <div className="card-overlay">
        <button
          className="overlay-button play-button"
          onClick={(e) => {
            e.stopPropagation();
            handleRunPipeline(pipeline);
          }}
          aria-label="Run Pipeline"
        >
          <FontAwesomeIcon icon={faPlay} />
        </button>
        <button
          className="overlay-button config-button"
          onClick={(e) => {
            e.stopPropagation();
            handleSelectPipeline(pipeline);
          }}
          aria-label="Configure Pipeline"
        >
          <FontAwesomeIcon icon={faCog} />
        </button>
      </div>
    </div>
  );

  return (
    <div className="landing-page">
      <h1>Configured Pipelines</h1>

      {/* Tag Filter Panel */}
      <div className="tag-filter-panel">
        {allTags.map(tag => (
          <div
            key={tag}
            className={`tag-box ${selectedTags.indexOf(tag) !== -1 ? 'selected' : ''} ${tag.replace(" ", "").toLowerCase() + '-tag'}`}
            onClick={() => toggleTag(tag)}
            role="button"
            tabIndex={0}
            onKeyPress={(e) => {
              if (e.key === 'Enter' || e.key === ' ') {
                toggleTag(tag);
              }
            }}
            aria-pressed={selectedTags.indexOf(tag) !== -1}
          >
            {tag}
          </div>
        ))}
      </div>

      {/* Pipeline List */}
      <div className="pipeline-list">
        {filteredPipelines.map(pipelineCard)}
      </div>

      {/* Add Pipeline Button */}
      <button
        onClick={handleAddPipeline}
        className="add-pipeline-button"
        aria-label="Add New Pipeline"
      >
        +
      </button>
    </div>
  );
};

export default LandingPage;
