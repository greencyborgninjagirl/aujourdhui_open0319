# 版本与分支管理

本文约定 **Beta 1.0** 之后在 GitHub 上的版本号、标签与分支用法，与 [`CHANGELOG.md`](../CHANGELOG.md) 配合使用。

---

## 版本号与标签

| 阶段 | 命名示例 | 说明 |
|------|----------|------|
| Beta | `v1.0.0-beta.1`、`v1.0.0-beta.2` | 对外可称「Beta 1.0」等；数字递增表示同一大 Beta 下的迭代 |
| 正式版（将来） | `v1.0.0`、`v1.1.0` | 语义化版本：主版本 · 次版本 · 修订 |

- **打标签**：在 `main` 上对已测试通过的提交使用 **附注标签**（annotated tag），例如：  
  `git tag -a v1.0.0-beta.1 -m "Beta 1.0"`  
  并 `git push origin v1.0.0-beta.1`。
- **GitHub Releases**：可在仓库 **Releases** 页面基于标签写说明，附 `CHANGELOG` 对应小节。

---

## 分支策略

- **`main`**：始终代表 **可部署、可对外说明的基线**；只合并已测试通过的内容。
- **新功能**：从 `main` 拉出 **`feature/简述`**（例：`feature/daily-artwork-theme`），开发自测后在 GitHub 提 **Pull Request**，审查与 CI（若有）通过后再 **合并进 `main`**。
- **小修 / 热修**：可用 **`fix/简述`** 或 **`bugfix/简述`**，同样经 PR 合并进 `main`。
- **大改 / 实验**：可用独立 **`feature/...`** 或临时分支名，避免在 `main` 上长期直接提交未验证的大块变更。

合并前建议在 PR 描述中写明 **动机、测试方式、是否需改部署/环境变量**；合并后在 [`CHANGELOG.md`](../CHANGELOG.md) 增加对应版本小节。

---

## 与文档的关系

- 产品级快照（如 Beta 形态）：[`STATUS_1.0_BETA.md`](./STATUS_1.0_BETA.md) 等可按大版本保留或迭代。
- 每一版对外可见的变更摘要：**以 `CHANGELOG.md` 为准**。

---

*若日后团队扩大，可在此补充「保护分支规则、CODEOWNERS」等，与 GitHub 设置同步。*
