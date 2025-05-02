from __future__ import annotations

import dataclasses
import os
from copy import deepcopy
from dataclasses import dataclass
from enum import Enum
from typing import Any, Type, TypeVar

from . import beaker_pb2 as pb2
from .common import to_lower_camel, to_nanoseconds, to_snake_case

__all__ = [
    "PathOrStr",
    "BeakerSortOrder",
    "BeakerAuthRole",
    "BeakerJobPriority",
    "BeakerWorkloadType",
    "BeakerWorkloadStatus",
    "BeakerDatasetFileAlgorithmType",
    "BeakerCancelationCode",
    "BeakerGpuType",
    "BeakerImageSource",
    "BeakerEnvVar",
    "BeakerDataSource",
    "BeakerDataMount",
    "BeakerResultSpec",
    "BeakerTaskResources",
    "BeakerTaskContext",
    "BeakerTaskSpec",
    "BeakerSpecVersion",
    "BeakerRetrySpec",
    "BeakerExperimentSpec",
    "BeakerConstraints",
    "BeakerJob",
    "BeakerWorkload",
    "BeakerExperiment",
    "BeakerTask",
    "BeakerImage",
    "BeakerCluster",
    "BeakerNode",
    "BeakerDataset",
    "BeakerGroup",
    "BeakerSecret",
    "BeakerOrganization",
    "BeakerUser",
    "BeakerEnvironment",
    "BeakerWorkspace",
]


PathOrStr = os.PathLike | str

BeakerJob = pb2.Job
BeakerWorkload = pb2.Workload
BeakerExperiment = pb2.Experiment
BeakerTask = pb2.Task
BeakerImage = pb2.Image
BeakerCluster = pb2.Cluster
BeakerNode = pb2.Node
BeakerDataset = pb2.Dataset
BeakerGroup = pb2.Group
BeakerSecret = pb2.Secret
BeakerOrganization = pb2.Organization
BeakerUser = pb2.User
BeakerEnvironment = pb2.Environment
BeakerWorkspace = pb2.Workspace


class BaseEnum(Enum):
    def as_pb2(self) -> Any:
        return self


E = TypeVar("E", bound="IntEnum")


class IntEnum(int, BaseEnum):
    @classmethod
    def from_any(cls: Type[E], value) -> E:
        if isinstance(value, str):
            return getattr(cls, value)
        else:
            return cls(value)


class StrEnum(str, BaseEnum):
    def __str__(self) -> str:
        return self.value


class BeakerSortOrder(IntEnum):
    descending = pb2.SortOrder.SORT_ORDER_DESCENDING
    ascending = pb2.SortOrder.SORT_ORDER_ASCENDING


class BeakerAuthRole(IntEnum):
    deactivated = pb2.AuthRole.AUTH_ROLE_DEACTIVATED
    scientist = pb2.AuthRole.AUTH_ROLE_SCIENTIST
    system = pb2.AuthRole.AUTH_ROLE_SYSTEM
    admin = pb2.AuthRole.AUTH_ROLE_ADMIN


class BeakerJobPriority(IntEnum):
    low = pb2.JobPriority.JOB_PRIORITY_LOW
    normal = pb2.JobPriority.JOB_PRIORITY_NORMAL
    high = pb2.JobPriority.JOB_PRIORITY_HIGH
    urgent = pb2.JobPriority.JOB_PRIORITY_URGENT


class BeakerWorkloadType(IntEnum):
    experiment = pb2.WorkloadType.WORKLOAD_TYPE_EXPERIMENT
    environment = pb2.WorkloadType.WORKLOAD_TYPE_ENVIRONMENT


class BeakerWorkloadStatus(IntEnum):
    submitted = pb2.WorkloadStatus.STATUS_SUBMITTED
    queued = pb2.WorkloadStatus.STATUS_QUEUED
    initializing = pb2.WorkloadStatus.STATUS_INITIALIZING
    running = pb2.WorkloadStatus.STATUS_RUNNING
    stopping = pb2.WorkloadStatus.STATUS_STOPPING
    uploading_results = pb2.WorkloadStatus.STATUS_UPLOADING_RESULTS
    canceled = pb2.WorkloadStatus.STATUS_CANCELED
    succeeded = pb2.WorkloadStatus.STATUS_SUCCEEDED
    failed = pb2.WorkloadStatus.STATUS_FAILED
    ready_to_start = pb2.WorkloadStatus.STATUS_READY_TO_START


class BeakerDatasetFileAlgorithmType(IntEnum):
    SHA256 = pb2.DatasetFile.ALGORITHM_TYPE_SHA256
    CRC32C = pb2.DatasetFile.ALGORITHM_TYPE_CRC32C

    def hasher(self):
        """
        Get a :mod:`hasher <hashlib>` object for the given algorithm.
        """
        import hashlib

        import google_crc32c

        if self == self.SHA256:
            return hashlib.sha256()
        elif self == self.CRC32C:
            return google_crc32c.Checksum()
        else:
            raise NotImplementedError(f"hasher() not yet implemented for {self.name}")


class BeakerCancelationCode(IntEnum):
    system_preemption = pb2.CancelationCode.CANCELATION_CODE_SYSTEM_PREEMPTION
    user_preemption = pb2.CancelationCode.CANCELATION_CODE_USER_PREEMPTION
    idle = pb2.CancelationCode.CANCELATION_CODE_IDLE
    manual = pb2.CancelationCode.CANCELATION_CODE_MANUAL
    timeout = pb2.CancelationCode.CANCELATION_CODE_TIMEOUT
    node_unavailable = pb2.CancelationCode.CANCELATION_CODE_NODE_UNAVAILABLE
    impossible_to_schedule = pb2.CancelationCode.CANCELATION_CODE_IMPOSSIBLE_TO_SCHEDULE
    sibling_task_failed = pb2.CancelationCode.CANCELATION_CODE_SIBLING_TASK_FAILED
    sibling_task_preemption = pb2.CancelationCode.CANCELATION_CODE_SIBLING_TASK_PREEMPTION
    healthcheck_failed = pb2.CancelationCode.CANCELATION_CODE_HEALTHCHECK_FAILED
    sibling_task_retry = pb2.CancelationCode.CANCELATION_CODE_SIBLING_TASK_RETRY


class BeakerGpuType(IntEnum):
    NVIDIA_H100 = pb2.GpuType.GPU_TYPE_NVIDIA_H100
    NVIDIA_A100_80GB = pb2.GpuType.GPU_TYPE_NVIDIA_A100_80GB
    NVIDIA_A100_40GB = pb2.GpuType.GPU_TYPE_NVIDIA_A100_40GB
    NVIDIA_L4 = pb2.GpuType.GPU_TYPE_NVIDIA_L4
    NVIDIA_RTX_A5000 = pb2.GpuType.GPU_TYPE_NVIDIA_RTX_A5000
    NVIDIA_RTX_A6000 = pb2.GpuType.GPU_TYPE_NVIDIA_RTX_A6000
    NVIDIA_RTX_8000 = pb2.GpuType.GPU_TYPE_NVIDIA_RTX_8000
    NVIDIA_T4 = pb2.GpuType.GPU_TYPE_NVIDIA_T4
    NVIDIA_P100 = pb2.GpuType.GPU_TYPE_NVIDIA_P100
    NVIDIA_P4 = pb2.GpuType.GPU_TYPE_NVIDIA_P4
    NVIDIA_V100 = pb2.GpuType.GPU_TYPE_NVIDIA_V100
    NVIDIA_L40 = pb2.GpuType.GPU_TYPE_NVIDIA_L40
    NVIDIA_L40S = pb2.GpuType.GPU_TYPE_NVIDIA_L40S
    NVIDIA_B200 = pb2.GpuType.GPU_TYPE_NVIDIA_B200


T = TypeVar("T", bound="_BeakerSpecBase")


class _BeakerSpecBase:
    @classmethod
    def from_json(cls: Type[T], data: dict[str, Any]) -> T:
        return cls(**cls.unjsonify(data))

    def to_json(self) -> dict[str, Any]:
        return self.jsonify(self)

    @classmethod
    def unjsonify(cls, x: Any) -> Any:
        if isinstance(x, dict):
            return {to_snake_case(key): cls.unjsonify(value) for key, value in x.items()}
        elif isinstance(x, Enum):
            return cls.jsonify(x.value)
        elif isinstance(x, (list, tuple, set)):
            return [cls.jsonify(x_i) for x_i in x]
        else:
            return x

    @classmethod
    def jsonify(cls, x: Any) -> Any:
        if dataclasses.is_dataclass(x):
            return {
                to_lower_camel(field.name): cls.jsonify(getattr(x, field.name))
                for field in dataclasses.fields(x)
                if getattr(x, field.name) is not None
            }
        elif isinstance(x, Enum):
            return cls.jsonify(x.name)
        elif isinstance(x, dict):
            return {key: cls.jsonify(value) for key, value in x.items()}
        elif isinstance(x, (list, tuple, set)):
            return [cls.jsonify(x_i) for x_i in x]
        else:
            return x


@dataclass
class BeakerImageSource(_BeakerSpecBase):
    beaker: str | None = None
    docker: str | None = None


@dataclass
class BeakerEnvVar(_BeakerSpecBase):
    name: str
    value: str | None = None
    secret: str | None = None


@dataclass
class BeakerDataSource(_BeakerSpecBase):
    beaker: str | None = None
    host_path: str | None = None
    weka: str | None = None
    result: str | None = None
    secret: str | None = None


@dataclass
class BeakerDataMount(_BeakerSpecBase):
    source: BeakerDataSource
    mount_path: str
    sub_path: str | None = None

    @classmethod
    def new(
        cls,
        mount_path: str,
        sub_path: str | None = None,
        beaker: str | None = None,
        host_path: str | None = None,
        weka: str | None = None,
        result: str | None = None,
        secret: str | None = None,
    ) -> BeakerDataMount:
        return cls(
            mount_path=mount_path,
            sub_path=sub_path,
            source=BeakerDataSource(
                beaker=beaker,
                host_path=host_path,
                weka=weka,
                result=result,
                secret=secret,
            ),
        )


@dataclass
class BeakerResultSpec(_BeakerSpecBase):
    path: str


@dataclass
class BeakerTaskResources(_BeakerSpecBase):
    cpu_count: float | None = None
    gpu_count: int | None = None
    memory: str | None = None
    shared_memory: str | None = None


@dataclass
class BeakerTaskContext(_BeakerSpecBase):
    cluster: str | None = None
    priority: BeakerJobPriority | None = None
    preemptible: bool | None = None


@dataclass
class BeakerConstraints(_BeakerSpecBase):
    cluster: list[str] | None = None
    hostname: list[str] | None = None


@dataclass
class BeakerTaskSpec(_BeakerSpecBase):
    image: BeakerImageSource
    context: BeakerTaskContext
    result: BeakerResultSpec | None
    constraints: BeakerConstraints | None = None
    name: str | None = None
    command: list[str] | None = None
    arguments: list[str] | None = None
    env_vars: list[BeakerEnvVar] | None = None
    datasets: list[BeakerDataMount] | None = None
    resources: BeakerTaskResources | None = None
    host_networking: bool = False
    replicas: int | None = None
    leader_selection: bool | None = False
    propagate_failure: bool | None = None
    propagate_preemption: bool | None = None
    synchronized_start_timeout: int | None = None
    timeout: int | None = None

    def __post_init__(self):
        # Convert timeouts to nanoseconds.
        if self.timeout is not None:
            self.timeout = to_nanoseconds(self.timeout)
        if self.synchronized_start_timeout is not None:
            self.synchronized_start_timeout = to_nanoseconds(self.synchronized_start_timeout)

        # Ensure commands/arguments are all strings.
        if self.command:
            self.command = [str(x) for x in self.command]
        if self.arguments:
            self.arguments = [str(x) for x in self.arguments]

    @classmethod
    def from_json(cls, data: dict[str, Any]) -> BeakerTaskSpec:
        kwargs: dict[str, Any] = {}
        if (d := data.pop("image", None)) is not None:
            kwargs.update(image=BeakerImageSource.from_json(d))
        if (d := data.pop("result", None)) is not None:
            kwargs.update(result=BeakerResultSpec.from_json(d))
        if (d := data.pop("context", None)) is not None:
            kwargs.update(context=BeakerTaskContext.from_json(d))
        if (d := data.pop("constraints", None)) is not None:
            kwargs.update(constraints=BeakerConstraints.from_json(d))
        if (d := data.pop("envVars", None)) is not None:
            kwargs.update(env_vars=[BeakerEnvVar.from_json(v) for v in d])
        if (d := data.pop("datasets", None)) is not None:
            kwargs.update(datasets=[BeakerDataMount.from_json(v) for v in d])
        if (d := data.pop("resources", None)) is not None:
            kwargs.update(resources=BeakerTaskResources.from_json(d))
        return cls(**cls.unjsonify(data), **kwargs)

    @classmethod
    def new(
        cls,
        name: str,
        cluster: str | list[str] | None = None,
        beaker_image: str | None = None,
        docker_image: str | None = None,
        result_path: str = "/unused",
        priority: BeakerJobPriority | str | None = None,
        preemptible: bool | None = None,
        **kwargs,
    ) -> BeakerTaskSpec:
        constraints = kwargs.pop("constraints", None)
        if constraints is not None and not isinstance(constraints, BeakerConstraints):
            constraints = BeakerConstraints(**constraints)

        if cluster is not None:
            if constraints is not None and constraints.cluster:
                raise ValueError("'cluster' can only be specified one way")
            if isinstance(cluster, list):
                if constraints is not None:
                    constraints.cluster = cluster
                else:
                    constraints = BeakerConstraints(cluster=cluster)
            elif isinstance(cluster, str):
                if constraints is not None:
                    constraints.cluster = [cluster]
                else:
                    constraints = BeakerConstraints(cluster=[cluster])

        return cls(
            name=name,
            image=BeakerImageSource(beaker=beaker_image, docker=docker_image),
            result=BeakerResultSpec(path=result_path),
            context=BeakerTaskContext(
                priority=None if priority is None else BeakerJobPriority.from_any(priority),
                preemptible=preemptible,
            ),
            constraints=constraints,
            **kwargs,
        )

    def with_image(self, **kwargs) -> BeakerTaskSpec:
        return dataclasses.replace(self, image=BeakerImageSource(**kwargs))

    def with_result(self, **kwargs) -> BeakerTaskSpec:
        return dataclasses.replace(self, result=BeakerResultSpec(**kwargs))

    def with_context(self, **kwargs) -> BeakerTaskSpec:
        return dataclasses.replace(self, context=BeakerTaskContext(**kwargs))

    def with_name(self, name: str) -> BeakerTaskSpec:
        return dataclasses.replace(self, name=name)

    def with_command(self, command: list[str | int | float]) -> BeakerTaskSpec:
        return dataclasses.replace(self, command=[str(c) for c in command])

    def with_arguments(self, arguments: list[str | int | float]) -> BeakerTaskSpec:
        return dataclasses.replace(self, arguments=[str(a) for a in arguments])

    def with_resources(self, **kwargs) -> BeakerTaskSpec:
        return dataclasses.replace(self, resources=BeakerTaskResources(**kwargs))

    def with_dataset(self, mount_path: str, **kwargs) -> BeakerTaskSpec:
        return dataclasses.replace(
            self, datasets=(self.datasets or []) + [BeakerDataMount.new(mount_path, **kwargs)]
        )

    def with_env_var(
        self, name: str, value: str | None = None, secret: str | None = None
    ) -> BeakerTaskSpec:
        return dataclasses.replace(
            self,
            env_vars=(self.env_vars or []) + [BeakerEnvVar(name=name, value=value, secret=secret)],
        )

    def with_constraint(self, **kwargs: list[str]) -> BeakerTaskSpec:
        constraints = (
            BeakerConstraints(**kwargs)
            if self.constraints is None
            else dataclasses.replace(self.constraints, **kwargs)
        )
        return dataclasses.replace(self, constraints=constraints)


class BeakerSpecVersion(StrEnum):
    v2 = "v2"
    v2_alpha = "v2-alpha"


@dataclass
class BeakerRetrySpec(_BeakerSpecBase):
    allowed_task_retries: int | None = None


@dataclass
class BeakerExperimentSpec(_BeakerSpecBase):
    version: BeakerSpecVersion = BeakerSpecVersion.v2
    description: str | None = None
    tasks: list[BeakerTaskSpec] = dataclasses.field(default_factory=list)
    budget: str | None = None
    retry: BeakerRetrySpec | None = None

    @classmethod
    def from_file(cls, path: PathOrStr) -> BeakerExperimentSpec:
        """
        Load an :class:`ExperimentSpec` from a YAML file.
        """
        import yaml

        with open(path) as spec_file:
            raw_spec = yaml.load(spec_file, Loader=yaml.SafeLoader)
            return cls.from_json(raw_spec)

    @classmethod
    def from_json(cls, data: dict[str, Any]) -> BeakerExperimentSpec:
        data = deepcopy(data)
        kwargs: dict[str, Any] = dict(
            tasks=[BeakerTaskSpec.from_json(t) for t in data.pop("tasks", [])]
        )
        if (version := data.pop("version", None)) is not None:
            kwargs.update(version=BeakerSpecVersion(version))
        if (d := data.pop("retry", None)) is not None:
            kwargs.update(retry=BeakerRetrySpec(**d))
        return cls(**cls.unjsonify(data), **kwargs)

    @classmethod
    def new(
        cls,
        *,
        budget: str | None = None,
        task_name: str = "main",
        description: str | None = None,
        cluster: str | list[str] | None = None,
        beaker_image: str | None = None,
        docker_image: str | None = None,
        result_path: str = "/unused",
        priority: BeakerJobPriority | str | None = None,
        **kwargs,
    ) -> BeakerExperimentSpec:
        return cls(
            budget=budget,
            description=description,
            tasks=[
                BeakerTaskSpec.new(
                    task_name,
                    cluster=cluster,
                    beaker_image=beaker_image,
                    docker_image=docker_image,
                    result_path=result_path,
                    priority=priority,
                    **kwargs,
                )
            ],
        )

    def to_file(self, path: PathOrStr) -> None:
        """
        Write the experiment spec to a YAML file.
        """
        import yaml

        raw_spec = self.to_json()
        with open(path, "wt") as spec_file:
            yaml.dump(raw_spec, spec_file, Dumper=yaml.SafeDumper)

    def with_task(self, task: BeakerTaskSpec) -> BeakerExperimentSpec:
        if task.name is not None:
            for other_task in self.tasks:
                if task.name == other_task.name:
                    raise ValueError(f"A task with the name '{task.name}' already exists")
        return dataclasses.replace(
            self,
            tasks=(self.tasks or []) + [task],
        )

    def with_description(self, description: str) -> BeakerExperimentSpec:
        return dataclasses.replace(self, description=description)

    def with_retries(self, allowed_task_retries: int) -> BeakerExperimentSpec:
        return dataclasses.replace(
            self, retry=BeakerRetrySpec(allowed_task_retries=allowed_task_retries)
        )
