import json
import logging
from typing import Any, Union

from ambient_backend_api_client import Command
from ambient_base_plugin import BasePlugin, ConfigPayload, Message, api_token_manager
from run_command_plugin.services.command_service import (
    CommandService,
    command_service_factory,
)


class RunCommandPlugin(BasePlugin):
    def __init__(self):
        self.cmd_svc = None
        self.logger = None

    async def configure(
        self, config: ConfigPayload, logger: Union[logging.Logger, Any] = None
    ) -> None:
        self.logger = logger or logging.getLogger(__name__)
        self.cmd_svc: CommandService = command_service_factory(
            logger=self.logger,
            node_id=config.node_id,
            platform=config.platform,
            plugin_config=config,
        )
        await self.cmd_svc.init()
        self.logger.info("RunCommandPlugin configured")

    @api_token_manager
    async def handle_event(self, message: Message, headers: dict = None) -> None:
        try:
            self.logger.info("Handling message for topic: {}", message.topic)

            msg_data: dict = json.loads(message.message)
            self.logger.debug(
                "RunCommandHanlder.handle - msg_data: {}",
                json.dumps(msg_data, indent=4),
            )

            cmd = Command.model_validate(msg_data)
            self.logger.debug("RunCommandHanlder.handle - cmd: {}", cmd)

            result = await self.cmd_svc.execute(cmd, api_headers=headers)
            self.logger.debug("RunCommandHanlder.handle - result: {}", result)

            self.logger.info(
                "Command executed {}",
                ("successfully" if result.is_ok() else "unsuccessfully"),
            )
        except Exception as e:
            self.logger.error("Error handling message: {}", e)
