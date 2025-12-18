# 贡献指南（Contributing）

感谢你愿意为 **HotelManager** 贡献代码。为了保持项目质量与一致性，请在提交 PR 前遵循以下约定。

## 1. 开发环境

- Python：>= 3.10
- 本项目默认不依赖第三方运行时库（仅标准库 + SQLite）

建议以可编辑模式安装（便于本地调试 CLI 脚本入口）：

```bash
python -m pip install -e .
```

如果你希望启用更严格的静态检查（可选 dev 依赖）：

```bash
python -m pip install -e .[dev]
```

## 2. 运行测试

本项目使用 `unittest` 与 `compileall` 作为最小化的质量门槛：

```bash
PYTHONPATH=src python -m compileall -q src tests
PYTHONPATH=src python -m unittest discover -s tests -v
```

> 说明：`PYTHONPATH=src` 让测试能直接引用 `src/` 下的包，不强制依赖安装步骤。

也可以使用脚本（有限任务，不会启动服务）：

```powershell
pwsh -NoLogo -NoProfile -File .\scripts\check.ps1
pwsh -NoLogo -NoProfile -File .\scripts\lint.ps1
```

```bash
bash ./scripts/check.sh
bash ./scripts/lint.sh
```

## 3. 代码风格与原则

- 业务规则放在 `services.py`（应用服务层），避免散落在 CLI / SQL 中
- SQL 与对象映射集中在 `repositories.py`
- CLI 层只做：参数解析、友好输出、调用服务层
- 避免引入“隐式回落逻辑”（出现异常时悄悄换另一套路径），错误要可预期、可定位

## 4. 提交粒度

鼓励 **原子提交**：

- 一个提交只做一件事
- 提交信息清晰（例如 `feat:` / `fix:` / `docs:` / `chore:` / `ci:`）
- 每次提交都能在 CI 中独立通过
