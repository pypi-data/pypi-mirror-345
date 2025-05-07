from __future__ import annotations

from digitalhub.entities.task._base.spec import TaskSpecWorkflow, TaskValidatorWorkflow


class TaskSpecKfpPipeline(TaskSpecWorkflow):
    """
    TaskSpecKfpPipeline specifications.
    """


class TaskValidatorKfpPipeline(TaskValidatorWorkflow):
    """
    TaskValidatorKfpPipeline validator.
    """
