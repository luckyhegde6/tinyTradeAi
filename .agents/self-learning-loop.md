# Self-Learning Loop

All AI Agents must follow this exact methodology when developing new features or fixing bugs in TinyTrade AI.

## 1. Plan
- Read `AGENTS.md`, `.agents/agent-memory.md`, and `.agents/Lessons.md`.
- Formulate a hypothesis or design a solution.
- Request user approval if the change is architectural.

## 2. Code
- Implement the change using minimal memory overhead.
- Follow the rules defined in `.agents/rules/`.

## 3. Test
- If it's API logic, use `curl` or MCP tooling (Playwright) against the local Flask server.
- If it's hardware logic, ensure the headless fallback works.
- NEVER test Playwright directly on the Orange Pi.

## 4. Evaluate
- Did the test pass?
- Check memory usage. Did we import a heavy library?
- If the test failed, read the logs, adjust the code, and go back to step 3.

## 5. Append Lesson
- If a mistake was made during the iteration that caused a crash or memory spike, document it in `.agents/Lessons.md`.
- Update `.agents/agent-memory.md` with the new state.

## 6. Loop
- Move to the next task in `.agents/todo/`.
