# Stepwise Learn 实施计划

> 面向实现者：本计划定义文件、接口与验证方式。技术判断留给实现者。

**Goal:** 一个本机可运行、离线可用的「一步步带你学知识」的 Web 应用，复刻 Sia 的四阶段教学法（提示 → 演练 → 检查站 → 测验）+ 白板逐步揭示 + 掌握度追踪 + 间隔复习，并留可插拔 AI 接口。

**Architecture:** 纯 Python 标准库 HTTP 服务 + SQLite 持久化 + 单页 HTML/CSS/JS 前端，零第三方依赖、零构建、离线可跑。教学法状态机与课程数据解耦；AI 大脑可插拔（离线规则引擎 / OpenAI 兼容 API）。服务端按「帧」下发板书与讲解，前端按帧逐步渲染。

**Tech Stack:** Python 3.12 标准库（http.server / sqlite3 / json / urllib）、原生 HTML+CSS+ES6、无框架、无 CDN。

**Spec:** 本文件 + `README.md`。

## Global Constraints
- 零第三方依赖；`python -X utf8` 直接启动；仅监听 127.0.0.1。
- 所有凭据走环境变量（`LEARN_API_BASE` / `LEARN_API_KEY` / `LEARN_MODEL`），不硬编码、不落盘、不写入日志；文档里用 `[API_KEY]` 占位。
- 离线模式必须能完整跑完四阶段；联网模式失败自动回退离线。
- 数据仅存本机 `data/learn.db`；不上传、不遥测。
- 教学法硬规则：提示阶段不给最终答案；答错回退到对应步骤并标记错步；掌握度按步骤追踪。
- 每个结论性产物必须能被自检脚本验证。

## File Structure
| 文件 | 职责 |
|---|---|
| `curriculum.py` | 课程包数据：知识点、分步揭示、常见错步、检查站、测验 |
| `pedagogy.py` | 四阶段状态机、帧生成、掌握度、SM-2 简化版间隔复习 |
| `brain.py` | 可插拔大脑：离线规则引擎 / OpenAI 兼容 API（自动回退） |
| `store.py` | SQLite：会话、事件、掌握度、复习队列 |
| `server.py` | HTTP 路由 + 静态文件 + JSON API |
| `static/index.html` | 单页前端：课程树、分步白板、检查站、测验、进度面板 |
| `selftest.py` | 端到端自检（状态机 + API + 掌握度 + 复习调度） |
| `start.py` / `start.bat` | 一键启动 |
| `README.md` | 使用说明、接 AI、复刻 Sia 的对照表 |

## Review Focus
1. **离线可用性**：无网络、无 API key 时四阶段必须完整可跑 → selftest 断言 `brain.mode == "offline"` 且帧序列含 4 个 phase。
2. **提示不泄答案**：hint 帧不含 `reveal` 文本 → selftest 断言。
3. **答错回退**：检查站答错后 `step_index` 回到对应步骤且 `wrong_steps` 增长 → selftest 断言。
4. **复习调度**：完成后 `reviews` 表出现记录且 `due_at > now`，答对推进间隔、答错重置为 1 天 → selftest 断言。
5. **凭据不外泄**：API 模式下日志/响应中不出现 key → selftest 断言 key 不在任何响应体。
6. **并发与脏数据**：同一会话重复 step 请求不产生重复掌握度记录 → selftest 断言幂等。

## Tasks
- [ ] T1 `curriculum.py` + 课程包（3 门课 × 3 知识点，含中文讲解与英文术语）
- [ ] T2 `pedagogy.py`：状态机 `Session.advance(action, payload) -> frame`，帧字段固定
- [ ] T3 `brain.py`：双模式 + 回退
- [ ] T4 `store.py`：4 张表 + 幂等写入
- [ ] T5 `server.py` + `static/index.html`：API 与白板渲染
- [ ] T6 `selftest.py` 覆盖 Review Focus 六条，实跑通过
- [ ] T7 `README.md` + 启动脚本，起服务用浏览器验收
