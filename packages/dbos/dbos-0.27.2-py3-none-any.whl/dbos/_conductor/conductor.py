import socket
import threading
import time
import traceback
from typing import TYPE_CHECKING, Optional

from websockets import ConnectionClosed, ConnectionClosedOK, InvalidStatus
from websockets.sync.client import connect
from websockets.sync.connection import Connection

from dbos._utils import GlobalParams
from dbos._workflow_commands import (
    get_workflow,
    list_queued_workflows,
    list_workflow_steps,
    list_workflows,
)

from . import protocol as p

if TYPE_CHECKING:
    from dbos import DBOS


class ConductorWebsocket(threading.Thread):

    def __init__(
        self, dbos: "DBOS", conductor_url: str, conductor_key: str, evt: threading.Event
    ):
        super().__init__(daemon=True)
        self.websocket: Optional[Connection] = None
        self.evt = evt
        self.dbos = dbos
        self.app_name = dbos.config["name"]
        self.url = (
            conductor_url.rstrip("/") + f"/websocket/{self.app_name}/{conductor_key}"
        )

    def run(self) -> None:
        while not self.evt.is_set():
            try:
                with connect(
                    self.url, open_timeout=5, logger=self.dbos.logger
                ) as websocket:
                    self.websocket = websocket
                    while not self.evt.is_set():
                        message = websocket.recv()
                        if not isinstance(message, str):
                            self.dbos.logger.warning(
                                "Received unexpected non-str message"
                            )
                            continue
                        base_message = p.BaseMessage.from_json(message)
                        msg_type = base_message.type
                        error_message = None
                        if msg_type == p.MessageType.EXECUTOR_INFO:
                            info_response = p.ExecutorInfoResponse(
                                type=p.MessageType.EXECUTOR_INFO,
                                request_id=base_message.request_id,
                                executor_id=GlobalParams.executor_id,
                                application_version=GlobalParams.app_version,
                                hostname=socket.gethostname(),
                            )
                            websocket.send(info_response.to_json())
                            self.dbos.logger.info("Connected to DBOS conductor")
                        elif msg_type == p.MessageType.RECOVERY:
                            recovery_message = p.RecoveryRequest.from_json(message)
                            success = True
                            try:
                                self.dbos._recover_pending_workflows(
                                    recovery_message.executor_ids
                                )
                            except Exception as e:
                                error_message = f"Exception encountered when recovering workflows: {traceback.format_exc()}"
                                self.dbos.logger.error(error_message)
                                success = False
                            recovery_response = p.RecoveryResponse(
                                type=p.MessageType.RECOVERY,
                                request_id=base_message.request_id,
                                success=success,
                                error_message=error_message,
                            )
                            websocket.send(recovery_response.to_json())
                        elif msg_type == p.MessageType.CANCEL:
                            cancel_message = p.CancelRequest.from_json(message)
                            success = True
                            try:
                                self.dbos.cancel_workflow(cancel_message.workflow_id)
                            except Exception as e:
                                error_message = f"Exception encountered when cancelling workflow {cancel_message.workflow_id}: {traceback.format_exc()}"
                                self.dbos.logger.error(error_message)
                                success = False
                            cancel_response = p.CancelResponse(
                                type=p.MessageType.CANCEL,
                                request_id=base_message.request_id,
                                success=success,
                                error_message=error_message,
                            )
                            websocket.send(cancel_response.to_json())
                        elif msg_type == p.MessageType.RESUME:
                            resume_message = p.ResumeRequest.from_json(message)
                            success = True
                            try:
                                self.dbos.resume_workflow(resume_message.workflow_id)
                            except Exception as e:
                                error_message = f"Exception encountered when resuming workflow {resume_message.workflow_id}: {traceback.format_exc()}"
                                self.dbos.logger.error(error_message)
                                success = False
                            resume_response = p.ResumeResponse(
                                type=p.MessageType.RESUME,
                                request_id=base_message.request_id,
                                success=success,
                                error_message=error_message,
                            )
                            websocket.send(resume_response.to_json())
                        elif msg_type == p.MessageType.RESTART:
                            restart_message = p.RestartRequest.from_json(message)
                            success = True
                            try:
                                self.dbos.restart_workflow(restart_message.workflow_id)
                            except Exception as e:
                                error_message = f"Exception encountered when restarting workflow {restart_message.workflow_id}: {traceback.format_exc()}"
                                self.dbos.logger.error(error_message)
                                success = False
                            restart_response = p.RestartResponse(
                                type=p.MessageType.RESTART,
                                request_id=base_message.request_id,
                                success=success,
                                error_message=error_message,
                            )
                            websocket.send(restart_response.to_json())
                        elif msg_type == p.MessageType.LIST_WORKFLOWS:
                            list_workflows_message = p.ListWorkflowsRequest.from_json(
                                message
                            )
                            body = list_workflows_message.body
                            infos = []
                            try:
                                infos = list_workflows(
                                    self.dbos._sys_db,
                                    workflow_ids=body["workflow_uuids"],
                                    user=body["authenticated_user"],
                                    start_time=body["start_time"],
                                    end_time=body["end_time"],
                                    status=body["status"],
                                    request=False,
                                    app_version=body["application_version"],
                                    name=body["workflow_name"],
                                    limit=body["limit"],
                                    offset=body["offset"],
                                    sort_desc=body["sort_desc"],
                                )
                            except Exception as e:
                                error_message = f"Exception encountered when listing workflows: {traceback.format_exc()}"
                                self.dbos.logger.error(error_message)

                            list_workflows_response = p.ListWorkflowsResponse(
                                type=p.MessageType.LIST_WORKFLOWS,
                                request_id=base_message.request_id,
                                output=[
                                    p.WorkflowsOutput.from_workflow_information(i)
                                    for i in infos
                                ],
                                error_message=error_message,
                            )
                            websocket.send(list_workflows_response.to_json())
                        elif msg_type == p.MessageType.LIST_QUEUED_WORKFLOWS:
                            list_queued_workflows_message = (
                                p.ListQueuedWorkflowsRequest.from_json(message)
                            )
                            q_body = list_queued_workflows_message.body
                            infos = []
                            try:
                                infos = list_queued_workflows(
                                    self.dbos._sys_db,
                                    start_time=q_body["start_time"],
                                    end_time=q_body["end_time"],
                                    status=q_body["status"],
                                    request=False,
                                    name=q_body["workflow_name"],
                                    limit=q_body["limit"],
                                    offset=q_body["offset"],
                                    queue_name=q_body["queue_name"],
                                    sort_desc=q_body["sort_desc"],
                                )
                            except Exception as e:
                                error_message = f"Exception encountered when listing queued workflows: {traceback.format_exc()}"
                                self.dbos.logger.error(error_message)

                            list_queued_workflows_response = (
                                p.ListQueuedWorkflowsResponse(
                                    type=p.MessageType.LIST_QUEUED_WORKFLOWS,
                                    request_id=base_message.request_id,
                                    output=[
                                        p.WorkflowsOutput.from_workflow_information(i)
                                        for i in infos
                                    ],
                                    error_message=error_message,
                                )
                            )
                            websocket.send(list_queued_workflows_response.to_json())
                        elif msg_type == p.MessageType.GET_WORKFLOW:
                            get_workflow_message = p.GetWorkflowRequest.from_json(
                                message
                            )
                            info = None
                            try:
                                info = get_workflow(
                                    self.dbos._sys_db,
                                    get_workflow_message.workflow_id,
                                    get_request=False,
                                )
                            except Exception as e:
                                error_message = f"Exception encountered when getting workflow {get_workflow_message.workflow_id}: {traceback.format_exc()}"
                                self.dbos.logger.error(error_message)

                            get_workflow_response = p.GetWorkflowResponse(
                                type=p.MessageType.GET_WORKFLOW,
                                request_id=base_message.request_id,
                                output=(
                                    p.WorkflowsOutput.from_workflow_information(info)
                                    if info is not None
                                    else None
                                ),
                                error_message=error_message,
                            )
                            websocket.send(get_workflow_response.to_json())
                        elif msg_type == p.MessageType.EXIST_PENDING_WORKFLOWS:
                            exist_pending_workflows_message = (
                                p.ExistPendingWorkflowsRequest.from_json(message)
                            )
                            pending_wfs = []
                            try:
                                pending_wfs = self.dbos._sys_db.get_pending_workflows(
                                    exist_pending_workflows_message.executor_id,
                                    exist_pending_workflows_message.application_version,
                                )
                            except Exception as e:
                                error_message = f"Exception encountered when checking for pending workflows: {traceback.format_exc()}"
                                self.dbos.logger.error(error_message)

                            exist_pending_workflows_response = (
                                p.ExistPendingWorkflowsResponse(
                                    type=p.MessageType.EXIST_PENDING_WORKFLOWS,
                                    request_id=base_message.request_id,
                                    exist=len(pending_wfs) > 0,
                                    error_message=error_message,
                                )
                            )
                            websocket.send(exist_pending_workflows_response.to_json())
                        elif msg_type == p.MessageType.LIST_STEPS:
                            list_steps_message = p.ListStepsRequest.from_json(message)
                            step_info = None
                            try:
                                step_info = list_workflow_steps(
                                    self.dbos._sys_db,
                                    self.dbos._app_db,
                                    list_steps_message.workflow_id,
                                )
                            except Exception as e:
                                error_message = f"Exception encountered when getting workflow {list_steps_message.workflow_id}: {traceback.format_exc()}"
                                self.dbos.logger.error(error_message)

                            list_steps_response = p.ListStepsResponse(
                                type=p.MessageType.LIST_STEPS,
                                request_id=base_message.request_id,
                                output=(
                                    [
                                        p.WorkflowSteps.from_step_info(i)
                                        for i in step_info
                                    ]
                                    if step_info is not None
                                    else None
                                ),
                                error_message=error_message,
                            )
                            websocket.send(list_steps_response.to_json())
                        else:
                            self.dbos.logger.warning(
                                f"Unexpected message type: {msg_type}"
                            )
                            unknown_message = p.BaseResponse(
                                request_id=base_message.request_id,
                                type=msg_type,
                                error_message="Unknown message type",
                            )
                            # Still need to send a response to the conductor
                            websocket.send(unknown_message.to_json())
            except ConnectionClosedOK:
                self.dbos.logger.info("Conductor connection terminated")
                break
            except ConnectionClosed as e:
                self.dbos.logger.warning(
                    f"Connection to conductor lost. Reconnecting: {e}"
                )
                time.sleep(1)
                continue
            except InvalidStatus as e:
                # This happens when it cannot open a connection to the conductor. E.g., the conductor rejects the request
                json_data = e.response.body.decode("utf-8")
                self.dbos.logger.error(
                    f"Failed to connect to conductor. Retrying: {str(e) }. Details: {json_data}"
                )
                time.sleep(1)
                continue
            except Exception as e:
                self.dbos.logger.error(
                    f"Unexpected exception in connection to conductor. Reconnecting: {e}"
                )
                time.sleep(1)
                continue
