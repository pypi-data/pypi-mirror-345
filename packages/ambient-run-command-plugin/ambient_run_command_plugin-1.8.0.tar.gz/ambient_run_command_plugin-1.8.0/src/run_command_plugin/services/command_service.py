import logging
import subprocess
from abc import ABC, abstractmethod
from typing import Optional

import aiohttp
from ambient_backend_api_client import (
    Command,
    CommandNodeRelationship,
    CommandStatusEnum,
)
from ambient_base_plugin import ConfigPayload
from result import Err, Ok, Result


class CommandService(ABC):
    @abstractmethod
    async def execute(self, command: Command) -> Result[None, str]:
        pass

    @abstractmethod
    async def init(self) -> None:
        """Initialize the command service."""


class CommandServiceLinux(CommandService):
    def __init__(
        self, logger: logging.Logger, node_id: int, plugin_config: ConfigPayload
    ):
        self.node_id = node_id
        self.logger = logger
        self.plugin_config = plugin_config
        self.logger.info("CommandServiceLinux initialized")

    async def init(self) -> None:
        self.logger.info("API config saved to CommandServiceLinux")

    async def execute(self, command: Command, api_headers: dict) -> Result[None, str]:
        self.logger.info(
            "Executing command: {}",
            command.command_str if command.shell else command.command_list,
        )

        # update status to running
        update_cmd_result = await self.update_command(
            command.id, self.node_id, CommandStatusEnum.RUNNING, api_headers
        )
        if update_cmd_result.is_err():
            err_msg = f"Failed to update command status to running: \
{update_cmd_result.unwrap_err()}"
            self.logger.error(err_msg)
            return update_cmd_result
        self.logger.debug(
            "CommandServiceLinux.execute - updated command status to running: {}",
            update_cmd_result.unwrap().model_dump_json(indent=4),
        )

        # Run the command
        self.logger.info("Running the command ...")
        result = self.run_command(command)
        if result.is_err():
            err_msg = f"Command failed: {result.unwrap_err()}"
            self.logger.error(err_msg)
            self.logger.debug("Updating command status failed: {}", err_msg)
            await self.update_command(
                command.id,
                self.node_id,
                CommandStatusEnum.FAILURE,
                result,
                api_headers,
            )
            return result
        self.logger.info("Command executed successfully.")
        self.logger.debug(
            "CommandServiceLinux.execute - command result: {}", result.unwrap()
        )

        # update result
        self.logger.info("Updating command status ...")
        update_result = await self.update_command(
            command.id,
            self.node_id,
            CommandStatusEnum.SUCCESS if result.is_ok() else CommandStatusEnum.FAILURE,
            result,
            api_headers,
        )
        if update_result.is_err():
            err_msg = f"Failed to update command status: {update_result.unwrap_err()}"
            self.logger.error(err_msg)
            return update_result
        self.logger.debug(
            "CommandServiceLinux.execute - updated command status: {}",
            update_result.unwrap().model_dump_json(indent=4),
        )
        self.logger.info("Command status updated successfully.")
        return Ok(None)

    async def update_command(
        self,
        command_id: int,
        node_id: int,
        status: CommandStatusEnum,
        api_headers: dict,
        result: Optional[Result[str, str]] = None,
    ) -> Result[CommandNodeRelationship, str]:
        self.logger.debug("grabbing new token from plugin config")
        async with aiohttp.ClientSession() as session:
            try:
                async with session.put(
                    f"{self.api_config.host}/commands/outputs",
                    json={
                        "node_id": node_id,
                        "command_id": command_id,
                        "status": status,
                        "error": (
                            result.unwrap_err()
                            if (result and result.is_err())
                            else None
                        ),
                        "output": (
                            result.unwrap() if (result and result.is_ok()) else None
                        ),
                    },
                    headers=api_headers,
                ) as response:
                    response.raise_for_status()
                    data = await response.json()
                    return Ok(CommandNodeRelationship.model_validate(data))
            except aiohttp.ClientResponseError as e:
                if e.status == 404:
                    return Err("Command not found")
                else:
                    err_msg = f"Failed to update command: {e}"
                    self.logger.error(err_msg)
                    return Err(err_msg)

    def run_command(self, command: Command) -> Result[str, str]:
        result: Optional[subprocess.CompletedProcess] = None
        try:
            self.logger.info(
                "Running command: {}",
                command.command_list if not command.shell else command.command_str,
            )
            self.logger.debug(
                "command context: WORKDIR={}, USER={}, ENV={}, TIMEOUT={}, SHELL={}",
                command.workdir,
                command.os_user,
                command.env_vars,
                command.timeout,
                command.shell,
            )
            result = subprocess.run(
                command.command_list if not command.shell else command.command_str,
                shell=command.shell,
                check=command.shell,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=command.timeout if command.timeout else None,
                cwd=command.workdir,
                user=command.os_user,
                env=command.env_vars,
                executable="/bin/bash",
            )
            self.logger.debug("run_command() - result: {}", result)
            output = result.stdout.decode("utf-8")
            if not output or output == "\n":
                self.logger.debug("run_command() - no output in stdout, using stderr")
                output = result.stderr.decode("utf-8")
            return Ok(output)
        except subprocess.CalledProcessError as e:
            err_msg = f"Command failed: [subprocess.CalledProcessError] - {e}"
            if result:
                self.logger.debug("result object exists")
                err_msg += f"\nstdout: {result.stdout.decode('utf-8')}"
                err_msg += f"\nstderr: {result.stderr.decode('utf-8')}"
            else:
                self.logger.debug("result object does not exist")
                err_msg += f"\nstdout: {e.stdout.decode('utf-8')}"
                err_msg += f"\nstderr: {e.stderr.decode('utf-8')}"
            self.logger.error(err_msg)
            return Err(err_msg)
        except Exception as e:
            err_msg = f"Command failed: {e}"
            self.logger.error(err_msg)
            return Err(err_msg)


def command_service_factory(
    logger: logging.Logger, node_id: int, platform: str, plugin_config: ConfigPayload
) -> CommandService:
    if platform == "linux":
        return CommandServiceLinux(logger, node_id, plugin_config)
    raise NotImplementedError(f"Platform {platform} not supported")
