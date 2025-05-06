# Workflow class

Provides a `Workflow` class and a `@stage` decorator that allow to define workflows
in a declarative fashion.

A [`Stage`](stage.md#stage-class) object is responsible for creating Hail Batch jobs and declaring outputs
(files or metamist analysis objects) that are expected to be produced. Each stage
acts on a [`Target`](targets.md#target-class), which can be of the following:

    * SequencingGroup - an individual Sequencing Group (e.g. the CRAM of a single sample)
    * Dataset - a stratification of SGs in this analysis by Metamist Project (e.g. all SGs in acute-care)
    * Cohort - a stratification of SGs in this analysis by Metamist CustomCohort
    * MultiCohort - a union of all SGs in this analysis by Metamist CustomCohort

A `Workflow` object plugs stages together by resolving dependencies between different levels accordingly. Stages are
defined in this package, and chained into Workflows by their inter-Stages dependencies. Workflow names are defined in
main.py, which provides a way to choose a workflow using a CLI argument.

::: cpg_flow.workflow.get_workflow

::: cpg_flow.workflow.run_workflow

::: cpg_flow.workflow.Workflow

::: cpg_flow.workflow.Action

::: cpg_flow.workflow.skip

::: cpg_flow.workflow.path_walk
