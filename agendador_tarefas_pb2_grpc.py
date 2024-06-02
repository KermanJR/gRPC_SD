# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc
import warnings

import agendador_tarefas_pb2 as agendador__tarefas__pb2

GRPC_GENERATED_VERSION = '1.64.0'
GRPC_VERSION = grpc.__version__
EXPECTED_ERROR_RELEASE = '1.65.0'
SCHEDULED_RELEASE_DATE = 'June 25, 2024'
_version_not_supported = False

try:
    from grpc._utilities import first_version_is_lower
    _version_not_supported = first_version_is_lower(GRPC_VERSION, GRPC_GENERATED_VERSION)
except ImportError:
    _version_not_supported = True

if _version_not_supported:
    warnings.warn(
        f'The grpc package installed is at version {GRPC_VERSION},'
        + f' but the generated code in agendador_tarefas_pb2_grpc.py depends on'
        + f' grpcio>={GRPC_GENERATED_VERSION}.'
        + f' Please upgrade your grpc module to grpcio>={GRPC_GENERATED_VERSION}'
        + f' or downgrade your generated code using grpcio-tools<={GRPC_VERSION}.'
        + f' This warning will become an error in {EXPECTED_ERROR_RELEASE},'
        + f' scheduled for release on {SCHEDULED_RELEASE_DATE}.',
        RuntimeWarning
    )


class TaskSchedulerStub(object):
    """Missing associated documentation comment in .proto file."""

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.Register = channel.unary_unary(
                '/taskscheduler.TaskScheduler/Register',
                request_serializer=agendador__tarefas__pb2.RegisterRequest.SerializeToString,
                response_deserializer=agendador__tarefas__pb2.RegisterResponse.FromString,
                _registered_method=True)
        self.Authenticate = channel.unary_unary(
                '/taskscheduler.TaskScheduler/Authenticate',
                request_serializer=agendador__tarefas__pb2.AuthRequest.SerializeToString,
                response_deserializer=agendador__tarefas__pb2.AuthResponse.FromString,
                _registered_method=True)
        self.ScheduleTask = channel.unary_unary(
                '/taskscheduler.TaskScheduler/ScheduleTask',
                request_serializer=agendador__tarefas__pb2.TaskRequest.SerializeToString,
                response_deserializer=agendador__tarefas__pb2.TaskResponse.FromString,
                _registered_method=True)
        self.GetTaskStatus = channel.unary_unary(
                '/taskscheduler.TaskScheduler/GetTaskStatus',
                request_serializer=agendador__tarefas__pb2.TaskStatusRequest.SerializeToString,
                response_deserializer=agendador__tarefas__pb2.TaskStatusResponse.FromString,
                _registered_method=True)
        self.ListTasks = channel.unary_unary(
                '/taskscheduler.TaskScheduler/ListTasks',
                request_serializer=agendador__tarefas__pb2.ListTasksRequest.SerializeToString,
                response_deserializer=agendador__tarefas__pb2.ListTasksResponse.FromString,
                _registered_method=True)
        self.ListHistory = channel.unary_unary(
                '/taskscheduler.TaskScheduler/ListHistory',
                request_serializer=agendador__tarefas__pb2.ListHistoryRequest.SerializeToString,
                response_deserializer=agendador__tarefas__pb2.ListHistoryResponse.FromString,
                _registered_method=True)


class TaskSchedulerServicer(object):
    """Missing associated documentation comment in .proto file."""

    def Register(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def Authenticate(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def ScheduleTask(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def GetTaskStatus(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def ListTasks(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def ListHistory(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_TaskSchedulerServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'Register': grpc.unary_unary_rpc_method_handler(
                    servicer.Register,
                    request_deserializer=agendador__tarefas__pb2.RegisterRequest.FromString,
                    response_serializer=agendador__tarefas__pb2.RegisterResponse.SerializeToString,
            ),
            'Authenticate': grpc.unary_unary_rpc_method_handler(
                    servicer.Authenticate,
                    request_deserializer=agendador__tarefas__pb2.AuthRequest.FromString,
                    response_serializer=agendador__tarefas__pb2.AuthResponse.SerializeToString,
            ),
            'ScheduleTask': grpc.unary_unary_rpc_method_handler(
                    servicer.ScheduleTask,
                    request_deserializer=agendador__tarefas__pb2.TaskRequest.FromString,
                    response_serializer=agendador__tarefas__pb2.TaskResponse.SerializeToString,
            ),
            'GetTaskStatus': grpc.unary_unary_rpc_method_handler(
                    servicer.GetTaskStatus,
                    request_deserializer=agendador__tarefas__pb2.TaskStatusRequest.FromString,
                    response_serializer=agendador__tarefas__pb2.TaskStatusResponse.SerializeToString,
            ),
            'ListTasks': grpc.unary_unary_rpc_method_handler(
                    servicer.ListTasks,
                    request_deserializer=agendador__tarefas__pb2.ListTasksRequest.FromString,
                    response_serializer=agendador__tarefas__pb2.ListTasksResponse.SerializeToString,
            ),
            'ListHistory': grpc.unary_unary_rpc_method_handler(
                    servicer.ListHistory,
                    request_deserializer=agendador__tarefas__pb2.ListHistoryRequest.FromString,
                    response_serializer=agendador__tarefas__pb2.ListHistoryResponse.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'taskscheduler.TaskScheduler', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))
    server.add_registered_method_handlers('taskscheduler.TaskScheduler', rpc_method_handlers)


 # This class is part of an EXPERIMENTAL API.
class TaskScheduler(object):
    """Missing associated documentation comment in .proto file."""

    @staticmethod
    def Register(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(
            request,
            target,
            '/taskscheduler.TaskScheduler/Register',
            agendador__tarefas__pb2.RegisterRequest.SerializeToString,
            agendador__tarefas__pb2.RegisterResponse.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)

    @staticmethod
    def Authenticate(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(
            request,
            target,
            '/taskscheduler.TaskScheduler/Authenticate',
            agendador__tarefas__pb2.AuthRequest.SerializeToString,
            agendador__tarefas__pb2.AuthResponse.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)

    @staticmethod
    def ScheduleTask(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(
            request,
            target,
            '/taskscheduler.TaskScheduler/ScheduleTask',
            agendador__tarefas__pb2.TaskRequest.SerializeToString,
            agendador__tarefas__pb2.TaskResponse.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)

    @staticmethod
    def GetTaskStatus(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(
            request,
            target,
            '/taskscheduler.TaskScheduler/GetTaskStatus',
            agendador__tarefas__pb2.TaskStatusRequest.SerializeToString,
            agendador__tarefas__pb2.TaskStatusResponse.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)

    @staticmethod
    def ListTasks(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(
            request,
            target,
            '/taskscheduler.TaskScheduler/ListTasks',
            agendador__tarefas__pb2.ListTasksRequest.SerializeToString,
            agendador__tarefas__pb2.ListTasksResponse.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)

    @staticmethod
    def ListHistory(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(
            request,
            target,
            '/taskscheduler.TaskScheduler/ListHistory',
            agendador__tarefas__pb2.ListHistoryRequest.SerializeToString,
            agendador__tarefas__pb2.ListHistoryResponse.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)