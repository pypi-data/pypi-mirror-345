from typing import Type

from vajra._native.core.scheduler.replica_schedulers import (
    BaseReplicaScheduler as BaseReplicaSchedulerC,
)
from vajra._native.core.scheduler.replica_schedulers import (
    DynamicChunkReplicaScheduler as DynamicChunkReplicaSchedulerC,
)
from vajra.core.scheduler.replica_schedulers.base_replica_scheduler import (
    BaseReplicaScheduler,
)
from vajra.core.scheduler.utils.execution_time_predictor_factory import (
    ExecutionTimePredictorFactory,
)


class DynamicChunkReplicaScheduler(BaseReplicaScheduler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, create_native_handle=False, **kwargs)

        # Use the factory to get the execution time predictor and its native implementation
        self.execution_time_predictor = (
            ExecutionTimePredictorFactory.get_execution_time_predictor(
                model_config=self.model_config,
                parallel_config=self.parallel_config,
                cache_config=self.cache_config,
            )
        )
        self.execution_time_predictor_capsule = (
            self.execution_time_predictor._native_execution_time_predictor.as_capsule()
        )

        self._native_handle = self._create_native_handle()
        # Initialize the execution time predictor capsule before calling super init for correct native initialization

    def _get_native_handle_impl(self) -> Type[BaseReplicaSchedulerC]:
        return DynamicChunkReplicaSchedulerC
