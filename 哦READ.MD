# k230-c

## 当前检查点：R5 条件 eMMC DAT 43 kΩ 上拉

本版仅将 R563–R570 的值由 47 kΩ 改为 43 kΩ CRCW020143K0FKED 候选，并绑定既有 CRCW0201 候选封装。**这是有条件的电路/封装检查点，不是生产版本，也不构成寿命、信号完整性或 ROM 启动资格结论。**

当前入口：`project/cad/recovery-physical-candidate/CMK230_Core_REVIEW.kicad_pro`（原理图同名 `.kicad_sch`）。保持 `project/` 内相对目录；根说明文件为 `哦READ.MD`。

## 本版范围与验证

- 恰好八个 DAT 上拉的 Value/Footprint 字段改变；DAT0–DAT7 到 VEMMC_IO 的连接、全部 254 个元件、457 个网络、1,509 个引脚/功能/类型/网络绑定及其他元件和装配属性保持不变
- 封装覆盖为 166 个已分配、88 个未分配；R33 仍为 270 kΩ，R528 仍默认 DNP，存储默认禁止
- 在必须另行成立的总电阻误差 ±10% 接受预算下，43 kΩ 对应 38.7–47.3 kΩ，位于该 Micron 家族规定的 10–50 kΩ 区间；原 47 kΩ 的同预算上限为 51.7 kΩ
- ±10% 是覆盖初始误差、温度、装配、老化和环境的应用接受要求，不是已证明的任意任务寿命保证
- 新 KiCad 9.0.2 ERC 为 0；独立原生导出和全属性比较通过。保留 47 kΩ、改动无关 R33、装上 R528、接错供电、丢失封装和不合格误差预算的负控均按预期拒绝
- CORE PG 材料仅为只读审查，包含 R3 到 R5 的不变图桥接证据；没有采纳 supervisor 方案，也没有宣称功能失效

源范围、计算、脚本、独立复核和 24 个变更文件清单见 `project/recovery/r5-dat43/`。源清单 SHA-256：`f823cfe471f18b033cac6a5e49e0779dbf70a6ecaa91d596b80d3d246bebc3a8`。

## 仍待关闭的边界

完整泄漏/内部上拉/地误差、DAT 高低阈值、驱动能力、波形、HS200 时序、部分上电、冷切换、ROM/OTP、精确订货/生命周期和实际任务寿命均未获得资格结论。小直流负载不能替代这些检查。

仍无完整六层核心板布局布线。38 × 38 mm、140 触点、1 mm 间距、恰好六个铜层、仅顶面贴装的约束保持不变。88 个封装缺口、整板容纳、DDR/PDN、叠层/HDI、工厂工艺、贴装、高温/上电和 DFM 仍待完成。历史独立夹具或八层试验不能作为整板验收。

R3 的电感体下铜/孔限制、R574 电气限制以及 R4 的 BGA 条件焊盘/装配边界仍有效；未改变启动介质、晶振或采纳普通偏置批次。旧生成器与审查文件中的 47 kΩ 属于旧分支，不是 R5 验收依据。

## 历史与完整性

本版继承 R4 提交 `efffb5ac666efe3f91147fa7ffbdc881264cd6d3`。各版范围与报告保留在 `project/recovery/r3-physical-coverage/`、`r4-bga-coverage/` 和 `r5-dat43/`；原恢复检查在 `validation/2026-10-03-restored/`。历史报告按原阶段解读。

24 个 R5 源变更文件及其清单保持原始字节；当前文件完整性以 `SHA256SUMS` 为准，逐版来源和排除项见 `PUBLICATION_PROVENANCE.json`。厂商 PDF/页面、图像和运行时文件不上传；必要的上游 MIT 版权许可声明保留，未扩大第三方授权。

## English summary

R5 changes only eight eMMC DAT pullup values and footprint fields. At a required, not yet lifetime-qualified ±10% total resistance budget, 43 kΩ spans 38.7–47.3 kΩ within the source 10–50 kΩ range. All 254 components, 457 nets, 1,509 bindings and population attributes are preserved; fresh ERC passes. Coverage is 166 assigned / 88 unassigned. CORE PG is review-only. Lifetime, leakage, SI, ROM behavior and complete six-layer board qualification remain open.
