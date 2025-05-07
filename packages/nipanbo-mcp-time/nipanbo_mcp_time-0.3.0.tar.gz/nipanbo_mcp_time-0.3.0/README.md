mcp测试文件

获取当前系统时间



# 启动方式 
> uv run -m nipanbo_mcp_educate_time.server

```json
{
  "mcpServers": {
    "get_time": {
      "name": "get_time",
      "type": "stdio",
      "isActive": true,
      "registryUrl": "",
      "command": "uv",
      "args": [
        "run",
        "-m",
        "nipanbo_mcp_educate_time.server"
      ]
    }
  }
}
```