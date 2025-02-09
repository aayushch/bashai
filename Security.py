# Copyright (c) 2025
# Licensed under the MIT License.
# See LICENSE file in the root directory of this source tree.
#
# Created by: [Aayush Chawla]
# Created on: February 7, 2025

from dataclasses import dataclass
from enum import Enum
from typing import Dict
from Logger import Logger
import json
import os
import shutil


class OperationType(Enum):
    READ = "read"
    WRITE = "write"
    DELETE = "delete"
    MODIFY = "modify"


@dataclass
class Operation:
    type: OperationType
    description: str
    requires_confirmation: bool


class SecurityManager:
    def __init__(self, logger: Logger):
        self.logger = logger
        self.config_path = os.path.expanduser("~/.bashai/security.json")
        self.dangerous_operations = self._load_security_config()

    def _load_security_config(self) -> Dict[str, Operation]:
        self.logger.info(f"Loading security config from {self.config_path}")
        if not os.path.exists(self.config_path):
            return self._create_default_config()  # @todo fail if no security
        with open(self.config_path, 'r') as f:
            config_dict = json.load(f)
        return {k: self._dict_to_operation(v) for k, v in config_dict.items()}

    def _operation_to_dict(self, operation: Operation) -> dict:
        """Convert Operation object to dictionary for JSON serialization."""
        return {
            "type": operation.type.value,  # Convert enum to string
            "description": operation.description,
            "requires_confirmation": operation.requires_confirmation
        }

    def _dict_to_operation(self, data: dict) -> Operation:
        """Convert dictionary back to Operation object."""
        return Operation(
            type=OperationType(data["type"]),  # Convert string back to enum
            description=data["description"],
            requires_confirmation=data["requires_confirmation"]
        )

    def _create_default_config(self) -> Dict[str, Operation]:
        """
        Copy default security config from package and return parsed operations.
        """
        # Get the package directory path
        package_dir = os.path.dirname(os.path.abspath(__file__))
        default_config_path = os.path.join(
            package_dir, "security.json")

        # Create config directory if it doesn't exist
        os.makedirs(os.path.dirname(self.config_path), exist_ok=True)

        # Copy default config to user's config location
        shutil.copy2(default_config_path, self.config_path)

        # Load and parse the copied config
        with open(self.config_path, 'r') as f:
            config_dict = json.load(f)

        return {k: self._dict_to_operation(v) for k, v in config_dict.items()}
