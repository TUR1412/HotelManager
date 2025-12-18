# Pull Request

## 变更说明

请用 1~3 句话说明本次变更解决什么问题 / 增加什么能力：

- 

## 类型

- [ ] fix：缺陷修复
- [ ] feat：新功能
- [ ] docs：文档更新
- [ ] chore：工程化/杂项
- [ ] ci：CI/流水线调整

## 自检清单

- [ ] 本地已通过：`PYTHONPATH=src python -m compileall -q src tests`
- [ ] 本地已通过：`PYTHONPATH=src python -m unittest discover -s tests -v`
- [ ] 如涉及 CLI：已验证 `python -m hotelmanager --version`
- [ ] 如涉及 DB：已验证旧数据库可 `init/doctor` 正常运行（迁移可重复执行）
- [ ] 文档已同步更新（README / docs）
- [ ] Changelog 已更新（面向用户的变更）

