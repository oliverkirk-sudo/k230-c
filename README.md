# k230-c

## 当前状态：R2.1 电路与封装增量检查点

本仓库保存 CM-K230 核心板的可编辑工程增量与验证证据。**这不是可直接生产的整板工程，也不是独立完整工程。**

- 依赖 v12 基线，SHA-256：`63dab93b8433b3a367571ec64b11568b9c81dc466e8d562ce2108b647d341e58`。该基线在本次发布时尚未恢复，仓库未包含它
- 当前原理图：`checkpoints/R2.1/payload/cad/recovery-physical-candidate/CMK230_Core_REVIEW.kicad_sch`
- 当前分支没有完整核心板 PCB。包内小型 PCB/Gerber 是封装几何与反例检验夹具，不能用于生产核心板
- 6 层 HDI、38 mm 外形、140 触点及单面贴装是待完成/验证的设计要求；不能据此认定当前工程已经实现

## 本次重新验证（2026-10-03）

- 输入 ZIP：2,293,882 字节，332 个成员 CRC 通过，325 个原始增量清单文件 SHA-256 全部匹配
- 输入 ZIP SHA-256：`4e23cf611b37900dab169f0b44da5974ae70c65bbcf7624c97ccb16688eb3b5b`
- KiCad 9.0.2 重新导出：254 个元件、1,509 个引脚绑定；与归档网表的元件/属性/网络/引脚功能/类型无差异
- 新 ERC：0 个错误、150 个警告，全部为 `footprint_link_issues`，原因是缺少 v12 封装库。历史文件中的 ERC 0 记录不能替代这次结果
- R528 默认 DNP 保持；R574 尚无已验证封装；默认禁止存储
- 高温、上电、时序、DDR、六层 HDI 布局布线、DFM 和工厂工艺资格验证尚未完成

新验证见 `validation/2026-10-03/`。`checkpoints/R2.1/` 中的原始验证报告是历史证据；除上述明确列出的项目外，未在本次重新执行。

## 内容与使用范围

保留可编辑 KiCad 原理图/符号/候选封装/独立测试 PCB、脚本、网表、夹具 CAM、历史工程审查及来源 URL/哈希。已去除运行时缓存、会话设置、日志和图像；未上传厂商 PDF、扫描页面、IBIS、凭证或内部工作记录。公开子集及改动由 `PUBLICATION_PROVENANCE.json` 和 `SHA256SUMS` 记录。没有为第三方内容新增授权。

本仓库的 R2.1 是经过筛选的公开源文件增量，不是原 ZIP 的逐字节副本。`delta-manifest.json` 已相应重建。缺少的历史渲染/来源图像与基线相关测试不能直接重跑。恢复并核实 v12 后，才可在单独工作副本上使用 `checkpoints/R2.1/apply_delta.py`；不要在唯一原件上应用。该脚本会先验证基线和每个保留的增量哈希，拒绝不匹配的已有修改。

TI 候选阻焊桥名义 80 µm；NXP 厂商示例名义 55 µm，KiCad 全局最小阻焊桥设为 75 µm 时可能合并开窗。必须核对实际 CAM 和板厂的铜/蚀刻/阻焊/钢网/贴装工艺能力。不得把孤立封装检查当作整板制造批准。

## English summary

R2.1 is a partial electrical/footprint recovery checkpoint requiring the missing v12 baseline. It is not a standalone project or a production release. The active candidate has no full-board PCB. The fresh KiCad 9.0.2 export matches the archived 254-component / 1,509-binding graph. Fresh ERC has zero errors and 150 missing-library footprint-link warnings. Historical reports are retained with their original scope and are not fresh passes.

Future validated engineering checkpoints will preserve repository history and include their stage, validation scope, remaining limitations and file hashes.
