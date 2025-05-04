"""
nonebot-plugin-github-webhook
一个用于接收 GitHub Webhook 并通过 OneBot 协议将推送通知转发到 QQ 群的服务。

作者: AptS-1547
GitHub: https://github.com/AptS-1547/nonebot-plugin-github-webhook

本文件是 nonebot-plugin-github-webhook 的插件入口文件。
"""

from nonebot.plugin import PluginMetadata

from .config import Config

__plugin_meta__ = PluginMetadata(
    name="nonebot-plugin-github-webhook",
    description="一个用于接收 GitHub Webhook 并通过 OneBot 协议将推送通知转发到 QQ 群的服务。",
    usage="none",
    type="application",
    homepage="https://github.com/AptS-1547/nonebot-plugin-github-webhook",
    config=Config,
    supported_adapters={"~onebot.v11"},
)
