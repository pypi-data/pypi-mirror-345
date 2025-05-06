import traceback
from typing import Optional

from sgqlc.operation import Operation

from ML_management import variables
from ML_management.graphql import schema
from ML_management.graphql.send_graphql_request import send_graphql_request
from ML_management.mlmanagement.batcher import Batcher
from ML_management.mlmanagement.metric_autostepper import MetricAutostepper
from ML_management.mlmanagement.visibility_options import VisibilityOptions
from ML_management.variables import DEFAULT_EXPERIMENT


class ActiveJob:
    """
    A context manager that allows for the execution of a task locally.

    This class provides a convenient way to run a job locally.

    """

    def __init__(self, secret_uuid):
        self.secret_uuid = secret_uuid

    def __enter__(self):
        op = Operation(schema.Mutation)
        base_query = op.start_job(secret_uuid=self.secret_uuid)
        base_query.name()
        base_query.experiment.name()
        _query_job_params(base_query)
        self.job = send_graphql_request(op=op, json_response=False).start_job
        variables.secret_uuid = self.secret_uuid
        return self.job

    def __exit__(self, exc_type, exc_val, exc_tb):
        Batcher().wait_log_metrics()
        exception_traceback = None
        message = None
        status = "SUCCESSFUL"
        if exc_type:
            exception_traceback = traceback.format_exc()
            message = ": ".join([exc_type.__name__, str(exc_val)])
            status = "FAILED"

        op = Operation(schema.Mutation)
        op.stop_job(
            secret_uuid=variables.secret_uuid, status=status, message=message, exception_traceback=exception_traceback
        )
        try:
            _ = send_graphql_request(op=op, json_response=False).stop_job
        finally:
            variables.secret_uuid = None
            MetricAutostepper().clear()


def start_job(
    job_name: Optional[str] = None, experiment_name: str = DEFAULT_EXPERIMENT, visibility=VisibilityOptions.PRIVATE
) -> ActiveJob:
    """
    Create local job.

    Parameters
    ----------
    job_name: str | None=None
        Name of the new job. If not passed, it will be generated.
    experiment_name: str = "Default"
        Name of the experiment. Default: "Default"
    visibility: VisibilityOptions
        Visibility of this job to other users. Default: PRIVATE.

    Returns
    -------
    ActiveJob
        Active job.

    Usage:
        with start_local_job('my-beautiful-job') as job:
            mlmanagement.log_metric(...)
            mlmanagement.log_artifacts(...)
    """
    op = Operation(schema.Mutation)
    op.create_local_job(job_name=job_name, experiment_name=experiment_name, visibility=visibility.name)
    secret_uuid = send_graphql_request(op=op, json_response=False).create_local_job
    return ActiveJob(secret_uuid)


def _query_job_params(base_query):
    base_query.params()
    base_query.params.gpu()
    base_query.params.models_schemas()
    base_query.params.list_role_model_params()
    base_query.params.list_role_data_params()
    base_query.params.list_role_data_params.data_params()
    base_query.params.list_role_data_params.role()
    base_query.params.list_role_model_params.model_params()
    base_query.params.list_role_model_params.role()
    base_query.params.executor_params()
    base_query.params.executor_params.executor_method_params()
    base_query.params.executor_params.executor_version_choice()
    base_query.executor_version.upload_model_modes()
