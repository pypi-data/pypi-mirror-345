"""
nonebot-plugin-github-webhook
一个用于接收 GitHub Webhook 并通过 OneBot 协议将推送通知转发到 QQ 群的服务。

作者: AptS-1547
GitHub: https://github.com/AptS-1547/nonebot-plugin-github-webhook

本文件是 nonebot-plugin-github-webhook 的配置文件。
"""

from pydantic import BaseModel, field_validator

class Config(BaseModel):
    weather_api_key: str
    weather_command_priority: int = 10
    weather_plugin_enabled: bool = True

    @field_validator("weather_command_priority")
    @classmethod
    def check_priority(cls, v: int) -> int:
        if v >= 1:
            return v
        raise ValueError("weather command priority must greater than 1")
