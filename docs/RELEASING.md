# 发布流程（Releasing）

> 本文档面向维护者，用于“可重复、可审计”地发布版本。

## 0. 前置：本地质量门槛

在仓库根目录执行：

```bash
PYTHONPATH=src python -m compileall -q src tests
PYTHONPATH=src python -m unittest discover -s tests -v
```

如果你启用了 ruff（可选 dev 依赖）：

```bash
python -m ruff format --check .
python -m ruff check .
```

## 1. 更新版本号

需要保持两个位置一致：

- `pyproject.toml` 的 `[project].version`
- `src/hotelmanager/__init__.py` 的 `__version__`

## 2. 更新变更记录

在 `CHANGELOG.md` 中新增版本段落（推荐放在 `Unreleased` 下方），包含：

- 面向用户的功能变化
- 潜在不兼容变更（如有）
- 迁移注意事项（如有）

## 3. 提交

```bash
git status
git commit -am "chore: release x.y.z"
```

或拆分提交也可以，但建议发布点保持清晰。

## 4. 打 tag 并推送

```bash
git tag -a vX.Y.Z -m "vX.Y.Z"
git push origin main --tags
```

## 5. GitHub Release

在 GitHub 上基于 `vX.Y.Z` tag 创建 Release，并把 `CHANGELOG.md` 对应版本内容作为 Release Notes。

