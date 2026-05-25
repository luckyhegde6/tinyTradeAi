# TinyTrade AI Agentic Swarm

Welcome, AI Assistant. You are now part of the TinyTrade AI development swarm.
This project runs on an ultra-low-memory embedded device (Orange Pi 2G-IOT with 256MB RAM). All your decisions MUST respect this severe hardware constraint.

## Architecture & Rules
1. **Memory Limitation**: No Pandas, no Transformers, no heavy ML models. We use `sqlite3`, `requests`, `vaderSentiment`, and `TextBlob`.
2. **Zero Trust Security**: The Telegram bot and all APIs must strictly validate input and enforce authorization.
3. **Agent State**: Before beginning any task, read `.agents/agent-memory.md` to understand the current context and blockers.
4. **Lessons Learned**: Before making architectural decisions, consult `.agents/Lessons.md` to avoid repeating past mistakes.

## Subagents
Depending on the task, you must assume the persona of a specific subagent. Read their directives in `.agents/subagents/`:
- `hardware_agent.md`: For OLED, LCD, I2C, and Orange Pi OS issues.
- `i2c_agent.md`: For I2C bus scanning, address conflicts, electrical verification.
- `ssh_agent.md`: For SSH access, SCP deployment, remote command execution.
- `session_agent.md`: For tmux session management and persistent terminal work.
- `test_agent.md`: For test pipelines, verification scripts, regression testing.
- `data_agent.md`: For fetching from APIs and parsing RSS.
- `ai_agent.md`: For NLP and Anomaly detection logic.
- `security_agent.md`: For Zero Trust enforcement and Telegram validation.

## Self-Learning Loop
When tasked with iterative development, follow the protocol defined in `.agents/self-learning-loop.md`.
Never blindly commit code without verifying it through the defined testing loop.

## MCP Tooling (Playwright)
When automated browser/API testing is required, you must run it locally on the developer machine (not the Orange Pi) using Playwright. Refer to `.agents/skills/mcp-playwright-testing.md`.

## Commit-Only Policy — User Performs All Git/Deploy Actions

**The AI agent MUST NEVER:**
- `git push` to any remote
- `git checkout` or switch branches
- Run deploy scripts (`_deploy.py`, `_deploy_updates.py`)
- Create pull requests
- Install CLI tools (`gh`, `git` extensions, etc.)
- Merge or rebase branches

**After making a commit, the agent MUST:**
1. Append clear, copy-paste-ready instructions to the end of its response telling the user what to do next.
2. Include ALL shell commands the user needs to run, in order, with brief explanations.

**Example instruction format:**
```
## Next Steps (for you to run)

1. Push to remote:
   git push origin <branch-name>

2. Deploy to Orange Pi:
   python scripts/_deploy_updates.py

3. Create a pull request on GitHub:
   gh pr create --title "<title>" --body "<body>"
   Then view at: https://github.com/luckyhegde6/tinyTradeAi/pulls

4. Wait for the PR to be reviewed and merged into main.
```
