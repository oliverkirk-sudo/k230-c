# k230-c

## 当前检查点：R11 九个 22 µF 条件源焊盘

本版为 C206/C207/C208、C212/C213/C214、C540/C552/C562 增加九个候选封装绑定，覆盖为 **230 个已分配、24 个未分配**。全部 254 个元件值及其他非封装属性、457 个网络、1,509 个引脚/网络/类型/功能绑定、DNP/BOM/on-board 标志保持不变。

当前工程入口为 `project/cad/recovery-physical-candidate/CMK230_Core_REVIEW.kicad_pro`，电路版本 RCV-R11。保持 `project/` 内相对目录；根说明文件为 `哦READ.MD`。

## 本版范围与验证

- C206–C208 保持 CPU 输出电容组；C212–C214 保持 KPU 输出组。C540/C552 保持 VDD1P1_DDR_IO 上各自 DRAM VDD2/VDDQ 局部作用；C562 保持 VDD1P8 上 VDD1 局部去耦。相同封装不合并这些物理和电气职责
- 候选为 Samsung CL31B226KPHNNNE：名义 22 µF、±10%、10 V、X7R、1206。采用适用的厂商 metric 3216±0.20 mm 回流行，未更改任何名义值
- 铜为两块 1.25 × 1.80 mm 矩形，中心 x=±1.475 mm，内隙 1.70 mm、外跨度 4.20 mm。该选择位于厂商范围内，属于工程中点而不是唯一规定图案
- 最大本体 3.40 × 1.80 mm、最大高度 1.80 mm；阻焊扩张 +0.05 mm、独立 1:1 锡膏仍为工程假设
- 4.85 × 2.45 mm courtyard 的线宽为 0.05 mm，已核验名义阻焊外包络到 courtyard 线内缘四边均为 0.25 mm；这不是厂商 courtyard 或工厂装配批准
- 独立 77 项检查通过：完整原理图与生成器变更范围、库归属、元件属性/网络、来源文件、几何、已保存/新原生 CAM 和源不可变性均已核验
- 新 KiCad 9.0.2 ERC 为 0；20 × 13 mm 六层单封装孤立夹具 DRC 规则违规与未连接项均为 0，铜/阻焊/锡膏各两个闪孔
- 六个独立负控通过，包括 CPU/KPU/DRAM 电源节点混接、courtyard 实际余量不足，以及 0.05 mm 铜间隙违反 0.20 mm 规则的原生 DRC 拒绝

详细清单、来源 URL/哈希、原生结果和独立审查见 `project/recovery/r11-22uf-source-lands/`。源清单与原始增量 ZIP 身份记录在 `PUBLICATION_PROVENANCE.json`。

## 保留的电气与工艺门槛

CPU/KPU 每组输出电容仍保留已采用的 30 µF 有效电容量设计条件。分配 22 µF 名义器件不能建立组合偏压/热/老化后的 Ceff 或转换器稳定性；DRAM 局部电容仍有各自的分配、位置、回流与 PDN 责任，不能自动计入远端稳压器电容量。

并行来源审查中的 47 µF 方案没有适用的精确 ±0.40 mm 长度回流行，其工程提案仍未选择、未绑定；FLOW 表没有替代回流推荐。输入电容组数量/值方案也未应用。

阻焊、锡膏、courtyard、放置/蚀刻/对位/钢网容差、转移效率和可靠性仍须工厂验证。孤立诊断网络和六层设置不代表完整 38 × 38 mm 核心板、已批准叠层或布线完成。

R10 的 DNP 锡膏派生策略继续保留；主设计变更后须重新核验适用输入和派生结果，尚未完成整板应用或钢网工艺资格。R528 保持 DNP，默认存储资格仍受禁止。前版 eMMC 有效电容量、磁珠热/偏置滤波、时钟和启动等门槛继续有效。

24 个封装缺口为 12 个输入电容、4 个 47 µF 输出电容、4 个振荡器负载电容、C815、2 个振荡器反馈电阻和 RTC 晶体。仍须完成 38 × 38 mm/140 触点/1 mm 间距/恰好六铜层/仅顶面贴装的完整布局布线，以及 DDR/PDN、启动、时钟、采购、热/电实测和 DFM 验证。

## 历史与完整性

本版继承 R10 提交 `05b3254a3c19f15cf78588ed8095e06ab68f32da`。50 个工程变更文件及清单保持最终公开源字节；来源审查原先缺失的脚本已恢复并通过清单哈希检查。报告路径已规范化，新 SVG 与诊断 Gerber 为本项目原生导出。厂商原件、内部笔记和运行时文件不上传，必要的上游 MIT 版权许可声明保留。

当前文件完整性以 `SHA256SUMS` 为准；逐版来源、排除项和检查点记录见 `PUBLICATION_PROVENANCE.json`。历史报告按其输入哈希和限定范围解读。

## English summary

R11 adds nine conditional 22 µF source-land assignments, reaching 230 assigned / 24 gaps. Values, complete electrical bindings and population flags remain unchanged. All 77 independent checks, fresh ERC, isolated fixture DRC and six negative controls pass. The 0.25 mm mask-to-courtyard clearance includes the stroke's inner edge. The 47 µF proposal and input-bank changes remain unapplied. Combined effective capacitance, full-board placement/routing and manufacturing qualification remain open.
