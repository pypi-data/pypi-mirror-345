### mcp server test


#### 初始化

~~~ shell 
uv init .
uv venv
source .venv/bin/activate
uv add "mcp[cli]" httpx
~~~


#### 本地测试验证
npx -y @modelcontextprotocol/inspector


#### 部署配置

{
    "mcp": {
        "servers": {
            "Filesystem Operations": {
                "command": "uvx",
                "args": [
                    "https://github.com/lazysGit/lazylee_mcp_test.git"
                ]
            }
        }
    }
}


