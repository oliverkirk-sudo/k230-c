# k230-c

## 当前检查点：R12 独立输入电容组候选，尚未提升为首选

本版新增独立候选电路 `project/cad/recovery-inputbank-candidate/CMK230_Core_REVIEW.kicad_pro`，版本 RCV-INBANK-R12。**原首选/比较基线 `project/cad/recovery-physical-candidate/` 及全部 1,417 个 R11 工程文件保持字节不变；本候选未获提升。** 根说明文件保持 `哦READ.MD`。

两者必须区分：R11 基线为 254 个元件、1,509 个绑定、230 个封装已分配/24 个缺口；R12 候选为 250 个元件、1,501 个绑定、238 个封装已分配/12 个缺口。两者均为 457 个网络，均无完整核心板布局布线或生产资格。

## 候选的精确电气修订

- C203/C210/C211/C216/C217/C220/C225/C230 八个输入位置改为 22 µF CL31B226KPHNNNE 候选值及已审查的 R11 源封装，pin 1 保持 VIN_5V、pin 2 保持 GND
- 仅移除 C204/C221/C226/C231。U22/U23 各保留两个局部大容量输入电容；U21/U24/U25/U26 各一个
- C205/C209/C215/C222/C227/C232 六个 100 nF 局部旁路的值、封装和连接保持不变
- 所有其他元件属性、网络/引脚功能/电气类型、库、原生装配状态和 no-connect 保持前版契约；JP1/R45/R47/R528 仍为 DNP，26 个来源声明仍为非 BOM/非板上元件
- 候选生成器在独立运行目录中重建相同的电气、装配、符号库与引脚 CSV 契约。新导出和重新生成后的 ERC 均为 0
- 16 个独立负控均拒绝，包括实际原理图错接输入网络、装上 R528，以及生成器漏掉保留电容后再经 KiCad 导出的错误

## 电容量、启动和面积代价

来源典型曲线与明确假设的筛查给出 5.5 V 下约 6.9246 µF/颗、13.8492 µF/对。初始容差、AC 响应、温度、老化与模型余量分别记录。**这些分离的典型曲线与示例余量不建立组合保证下限或寿命资格**；3 µF/8 µF 输入设计条件尚需实际条件核验。

名义输入大容量总值由 **120 µF 增至 176 µF**，六个 100 nF 旁路不计入这两个总数。充电/浪涌、源阻抗、VIN 振铃、RMS 电流和纹波热必须复核。TPS628640B 在 UVLO 以下的 VIN 下降速率要求仍是明确集成门槛，Ceff 筛查有利不代表已满足。

在相同假设下比较的来源占位增加约 **34.40–36.08 mm²**，即使元件数减少。实际选用的八个 4.85 × 2.45 mm courtyard 中心线矩形总面积是 **95.06 mm²**；计入 0.05 mm 线宽的外包络是 **98.00 mm²**。三种面积指标不同，均不证明 38 mm 板上可放下、回路质量、访问空间或布线可行性。

## 来源、可视检查与边界

详细证据见 `project/recovery/r12-input-bank-candidate/`。来源审查最初绑定 R10；明确的 R10→R11 范围桥接独立核验 34 个输入/稳压器/分压/旁路位置不变，不宣称整个 master 哈希相同。

两张 PNG 为本项目原生 KiCad SVG 的裁切渲染，已检查像素和来源：CORE 单输入与 CPU 双输入均保留局部 100 nF 旁路。它们不是厂商页面或 GUI 截图，也不证明硬件与布局资格。

候选剩余 12 个封装缺口为 C41–C44、R41/R42、Y1、C201/C218/C223/C228 与 C815。组合 Ceff、VIN 下降、启动/瞬态、电流/热、稳定性、PDN、47 µF 焊盘、RTC 精度/启动、存储 BootROM/OTP、内存采购及整板工艺仍未关闭。R10 锡膏策略须针对实际最终板和装配输入重新核验。

完整设计仍受 38 × 38 mm、140 触点、1 mm 间距、恰好六铜层和仅顶面贴装约束。本候选尚未取代保留的首选基线，也不是制造发布。

## 历史与完整性

本版继承 R11 提交 `1e4e2832b2931a4de387179190fd21869681db39`。61 个新增工程文件及清单保持最终公开源字节；所有既有工程文件未改动。报告路径已规范化；厂商原件、内部笔记与运行时文件不上传，必要的上游 MIT 版权许可声明保留。

当前文件完整性以 `SHA256SUMS` 为准；逐版来源、排除项和检查点记录见 `PUBLICATION_PROVENANCE.json`。历史报告按输入哈希与范围解读；候选目录内继承的 PHYSICAL_STAGE.md 仅是历史上下文。

## English summary

R12 adds an unpromoted sibling input-bank circuit: eight value/footprint changes and four removals, yielding 250 components / 1501 bindings / 238 assigned footprints / 12 gaps. The preferred R11 baseline and all 1417 prior project files remain unchanged. Fresh and regenerated ERC pass with 16 negative rejections. Nominal input bulk rises 120→176 µF; combined guaranteed Ceff, inrush/falling VIN and the 34.40–36.08 mm² matched-area cost remain explicit gates. Full-board fit, routing and manufacturing are unqualified.
