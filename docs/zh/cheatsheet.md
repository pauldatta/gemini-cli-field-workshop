# Gemini CLI 速查表

> 涵盖本次工作坊所有内容的快速参考。
>
> *最后更新：2026-05-05 · [来源已与 gemini-cli 仓库核对](https://github.com/google-gemini/gemini-cli)*

---
## 安装

```bash
npm install -g @google/gemini-cli
gemini                     # Launch interactive mode
gemini --version           # Check version
```

---
## 键盘快捷键

| 快捷键 | 操作 |
|---|---|
| `Tab` | 接受建议的编辑 |
| `Shift+Tab` | 循环切换选项 |
| `Ctrl+G` | 外部编辑器（编辑提示词或计划） |
| `Ctrl+C` | 取消当前操作 |
| `↑` / `↓` | 导航提示词历史记录 |

---
## 斜杠命令

| 命令 | 描述 |
|---|---|
| `/plan` | 切换计划模式（只读研究） |
| `/stats` | 显示令牌使用情况和模型信息 |
| `/clear` | 清除上下文并重新开始 |
| `/tools` | 列出可用工具 |
| `/resume` | 恢复之前的会话 |
| `/rewind` | 回滚到之前的状态 |
| `/restore` | 从检查点恢复（需要[启用检查点](https://github.com/google-gemini/gemini-cli/blob/main/docs/cli/checkpointing.md)） |
| `/memory show` | 显示保存的记忆 |
| `/memory add "..."` | 添加记忆 |
| `/hooks panel` | 显示钩子执行状态 |
| `/skills list` | 列出可用技能 |
| `/extensions list` | 列出已安装的扩展 |
| `/commands` | 列出自定义命令 |

---
## 无头模式

```bash
# Simple prompt
gemini -p "Explain this code"

# Structured output
gemini -p "List endpoints as JSON" --output-format json

# Pipe input
cat error.log | gemini -p "Diagnose this error"

# Pipe code
cat file.js | gemini -p "Review this code for bugs"
```

---
## GEMINI.md 层级结构

```
~/.gemini/GEMINI.md          # Global preferences
./GEMINI.md                  # Project conventions
./backend/GEMINI.md          # Subdirectory rules
./frontend/GEMINI.md         # Subdirectory rules
```

### 导入语法
```markdown
@./docs/coding-standards.md
@./docs/architecture.md
```

> 请参阅 [GEMINI.md 参考文档](https://github.com/google-gemini/gemini-cli/blob/main/docs/cli/gemini-md.md) 获取完整语法。

---
## 子代理

```
# Built-in
@codebase_investigator Map the call chain for the login endpoint

# Custom (defined in .gemini/agents/)
@security-scanner Review auth middleware for vulnerabilities
```

### 子代理定义 (`.gemini/agents/my-agent.md`)
```markdown
---
model: gemini-3.1-flash-lite-preview
tools:
  - read_file
  - list_directory
---
You are a specialist in...
```

---
## Conductor 扩展

```bash
# Install
gemini extensions install https://github.com/gemini-cli-extensions/conductor

# Set up project context
/conductor:setup prompt="Project description..."

# Create a feature track
/conductor:newTrack prompt="Feature description..."

# Implement the current track
/conductor:implement
```

---
## 策略引擎 (TOML)

```toml
# Deny reading secrets
[[rule]]
toolName = "read_file"
argsPattern = '"file_path":".*\.env"'
decision = "deny"
priority = 100
deny_message = "Reading .env files is not allowed."

# Allow running tests
[[rule]]
toolName = "run_shell_command"
commandPrefix = "npm test"
decision = "allow"
priority = 50

# Default: ask human
[[rule]]
toolName = "*"
decision = "ask_user"
priority = 1
```

> 请参阅[策略引擎参考](https://github.com/google-gemini/gemini-cli/blob/main/docs/reference/policy-engine.md)以获取完整模式，以及参阅[使用策略引擎保护 Gemini CLI](https://aipositive.substack.com/p/secure-gemini-cli-with-the-policy)以获取实战演练。

---
## 钩子

### settings.json 钩子配置
```json
{
  "hooks": {
    "BeforeTool": [{
      "matcher": "write_file|replace",
      "hooks": [{
        "name": "my-hook",
        "type": "command",
        "command": "$GEMINI_PROJECT_DIR/.gemini/hooks/my-hook.sh",
        "timeout": 3000
      }]
    }]
  }
}
```

### 钩子脚本模板
```bash
#!/usr/bin/env bash
input=$(cat)
filepath=$(echo "$input" | jq -r '.tool_input.file_path // ""')

# Allow (default)
echo '{}'

# Deny with reason
echo '{"decision":"deny","reason":"Blocked because..."}'

# Inject context
echo '{"systemMessage":"Remember to..."}'
```

### 钩子事件
```
SessionStart → BeforeAgent → BeforeModel → BeforeToolSelection →
AfterModel → BeforeTool → AfterTool → AfterAgent → PreCompress →
Notification → SessionEnd
```

> 请参阅 [钩子参考](https://github.com/google-gemini/gemini-cli/blob/main/docs/hooks/index.md) 了解完整的事件生命周期。

---
## MCP 服务器

```json
{
  "mcpServers": {
    "github": {
      "command": "npx",
      "args": ["-y", "github-mcp-server"],
      "env": {
        "GITHUB_PERSONAL_ACCESS_TOKEN": "$GITHUB_TOKEN"
      }
    }
  }
}
```

---
## GitHub Actions

```yaml
- uses: google-github-actions/run-gemini-cli@v1
  with:
    prompt: "Review this PR for code quality and security"
```

---
## 身份验证选项

```bash
# Personal (free tier)
gemini   # OAuth flow

# Vertex AI (enterprise)
gcloud auth application-default login
# + configure .gemini/settings.json with auth.provider = "vertex-ai"
```

---
## 实用模式

```bash
# Smart commit
git diff --cached | gemini -p "Generate a conventional commit message"

# Code review
git diff main...HEAD | gemini -p "Review these changes"

# Generate docs
gemini -p "Generate JSDoc for all exports in backend/controllers/"

# Batch processing
for f in src/*.js; do gemini -p "Add TypeScript types" < "$f"; done
```

---
## 扩展

```bash
# Install from GitHub
gemini extensions install https://github.com/owner/repo

# Install a specific version
gemini extensions install https://github.com/owner/repo --ref v1.2.0

# List installed extensions
gemini extensions list
/extensions list   # from interactive mode

# Update all extensions
gemini extensions update --all

# Create from a template
gemini extensions new my-extension mcp-server

# Develop locally (symlink — changes reflected immediately)
gemini extensions link .

# Disable for this workspace only
gemini extensions disable my-extension --scope workspace
```

### 知名社区扩展

```bash
# Conductor (spec-driven development) — already in UC1
gemini extensions install https://github.com/gemini-cli-extensions/conductor

# Superpowers (TDD, code review, subagent-driven development)
gemini extensions install https://github.com/obra/superpowers

# Oh-My-Gemini-CLI (multi-agent orchestration framework)
gemini extensions install https://github.com/Joonghyun-Lee-Frieren/oh-my-gemini-cli

# Google Workspace CLI (optional — requires Workspace auth)
gemini extensions install https://github.com/googleworkspace/cli
```

### 扩展库

浏览社区扩展：[geminicli.com/extensions/browse](https://geminicli.com/extensions/browse/)

发布您自己的扩展：将 `gemini-cli-extension` 主题添加到您的 GitHub 仓库，并标记一个发布版本。
