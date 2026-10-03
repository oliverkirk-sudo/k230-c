# k230-c

## 当前检查点：已恢复 v12 + R2.1 源工程

本仓库保存 CM-K230 核心板的可编辑源工程和验证证据。v12 基线与 R2.1 累积增量均已恢复并核验。**这是原理图/候选封装恢复检查点，不是生产版本。当前候选仍没有完整核心板 PCB。**

当前入口：`project/cad/recovery-physical-candidate/CMK230_Core_REVIEW.kicad_pro`（原理图同名 `.kicad_sch`）。保持 `project/` 内相对目录结构即可解析已恢复的 10 个封装库。

## 本次重新验证（2026-10-03，KiCad 9.0.2）

- v12 ZIP：888 个成员 CRC 通过，886 个原始保留文件哈希匹配；SHA-256 `63dab93b8433b3a367571ec64b11568b9c81dc466e8d562ce2108b647d341e58`
- R2.1 ZIP：332 个成员 CRC 通过，325 个增量文件哈希匹配；SHA-256 `4e23cf611b37900dab169f0b44da5974ae70c65bbcf7624c97ccb16688eb3b5b`
- 增量在独立 v12 工作副本上通过防覆盖校验后应用，全部 325 个增量文件保持一致
- 新导出网表：254 个元件、1,509 个引脚绑定，与 R2.1 归档的元件、属性、网络、引脚功能和类型一致
- 恢复后新 ERC：0 个错误、0 个警告；10 个封装库均能解析
- R528 保持默认 DNP，存储默认禁止；149 个元件有封装字段，105 个仍未分配。R574 封装尚未完成验证

新结果在 `validation/2026-10-03-restored/`。`validation/2026-10-03-delta-only/` 保存基线尚未到达时的历史检查（0 错误、150 个缺库警告）；这些缺库警告已由完整恢复后的新结果取代。`project/` 中其他报告保留历史阶段含义，不能视为本次全部重新执行。

## 尚未完成的工程资格验证

- 当前 `recovery-physical-candidate` 没有完整核心板 PCB；历史 PCB、8 层试验和封装/负控夹具仍保留用于追溯，不是当前 6 层成品
- 38 × 38 mm 外形、140 个触点、1 mm 间距、恰好 6 个铜层及仅顶面贴装是设计要求，并非已达成的制造验收
- 尚需完成封装缺口、整板布局布线、DDR/时序、高温/上电、DFM 和工厂工艺确认
- TI 候选阻焊桥名义 80 µm；NXP 示例名义 55 µm。KiCad 全局最小阻焊桥设为 75 µm 时可能合并开窗。必须核对实际 CAM 与铜/蚀刻/阻焊/钢网/贴装能力

## 发布内容、来源与完整性

`project/` 保留源 CAD、库、脚本、数据、网表、工程审查和来源 URL/哈希，以及必要的 `LICENSE-01studio.txt` 上游 MIT 版权许可声明。未将该许可扩展为对其他第三方材料的新授权。

本公开源文件检查点经过筛选，未包含厂商 PDF/扫描页面、图像、运行时缓存、会话设置、日志、备份 ZIP 及部分大型历史 DDR 搜索生成结果。它不是两个原始 ZIP 的逐字节镜像。历史报告和冻结清单可能引用这些省略文件；需要相关生成结果的旧测试须先重新生成。完整排除项/原始哈希/两处非技术署名编辑见 `PUBLICATION_PROVENANCE.json`；当前发布文件完整性以根目录 `SHA256SUMS` 为准。

## English summary

The verified v12 baseline plus R2.1 delta has been restored. The active editable schematic resolves all 10 footprint libraries. Fresh KiCad 9.0.2 ERC has zero errors and zero warnings; the exported 254-component / 1,509-binding graph matches R2.1. There are 149 assigned and 105 unassigned component footprints. This is a source-recovery checkpoint, not a production release: no complete active six-layer board has been recovered or routed. Historical trials and tests retain their original limited scope.
