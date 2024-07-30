#!/usr/bin/env python3

from dataclasses import dataclass
from praline.config import AppConfigBase


@dataclass
class AppConfig(AppConfigBase):
    server_address: str = None
    threads: int = None


def main():
    app_config: AppConfig = AppConfig.load(config="example.yaml")
    print(f"Server: {app_config.server_address}")
    print(f"Threads: {app_config.threads}")


if __name__ == "__main__":
    exit(main())
