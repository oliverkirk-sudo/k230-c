# k230-c

## 当前检查点：R7 连接器件与板上铜特征

本版增加十个候选封装绑定，并将 JP1、TP81、TP82 三个板上铜特征排除出 BOM。覆盖为 **202 个已分配、52 个未分配**。全部 254 个元件值、457 个网络、1,509 个引脚/功能/类型/网络绑定、on-board 和 DNP 状态保持 R6 状态。仍无完整六层核心板，诊断 CAM 不是制造发布。

当前入口：`project/cad/recovery-physical-candidate/CMK230_Core_REVIEW.kicad_pro`（原理图同名 `.kicad_sch`）。保持 `project/` 内相对目录；根说明文件为 `哦READ.MD`。

## 本版范围与验证

- 恰好十个 Footprint 字段改变：R205/R206、R220/R221/R401/R528/R561、JP1、TP81/TP82；仅 JP1/TP81/TP82 的 BOM 标志由包含变为排除，根原理图版本标签变为 RCV-R7
- R205/R206 使用既有 TNPW 候选；R221/R401/R528 使用既有 CRCW 候选；新增 WSL/WFZ 条件铜焊盘，同时明确本体、courtyard、阻焊和锡膏的工程假设
- JP1 保持默认开路与 DNP，两块铜焊盘保留 MODE_TF/VDD_3V3 网络；只允许断电并放电后改变人工焊桥，启动/OTP 和存储电压资格仍未建立
- TP81/TP82 为顶面 0.8 mm 无钻孔、无锡膏观察焊盘，保持原 PMU 状态网络。三个铜特征均保留电路/板上身份，并从 BOM/PnP 排除
- JP1、R45、R47、R528 保持 DNP；R5 的八个条件 43 kΩ DAT 上拉、R33 的 270 kΩ 以及默认存储禁止状态保持不变
- 新 KiCad 9.0.2 ERC 为 0；五参考几何夹具 DRC 为 0。独立十参考夹具为零规则违规，保留共享网络导致三个预期未布线连接
- 独立原生导出与完整原理图结构复核通过；铜/阻焊/锡膏为 18/18/14 个闪孔，位置文件仅含六个应装电阻。失去 DNP、BoardOnly 误设、位置/BOM 误纳入等负控按预期拒绝

详细清单、来源 URL/哈希、原生结果与独立审查见 `project/recovery/r7-links-and-features/`。源清单哈希及原始增量 ZIP 哈希记录在 `PUBLICATION_PROVENANCE.json`。

## 装配与钢网的明确门槛

**KiCad 默认 F.Paste 导出仍包含 R528 的两个锡膏开口，即使 R528 为 DNP 且不在贴装位置文件中。** DNP 或 BOM/PnP 排除不等于钢网排除。制造前必须明确装配/钢网版本，并检查实际生成的锡膏输出；其他 DNP 元件也必须纳入相同策略。JP1/TP81/TP82 本身无锡膏开口。此处 Gerber 仅用于诊断。

## 保留的工程限制

52 个封装缺口为 40 个电容、9 个磁珠、2 个晶振反馈电阻和 RTC 晶体。电容热/偏压/老化后的有效值、时钟、复位/PG 裕量、存储启动策略、元件采购和热限制仍须关闭。

前版精度/寿命、热电阻/电流、R401 输入/固件、R221 支路电流和 R528 启动电压门槛持续有效。L21 与 Murata 电感各自的源几何和布线限制不能互相替代；开关回路、回流、耦合、EMI 和热仍待验证。

两套夹具均无完整电路路线或平面，通过不等于整板、电源回路或制造通过。仍须完成 38 × 38 mm/140 触点/1 mm 间距/恰好六铜层/仅顶面贴装的完整布局布线，以及 DDR/PDN、工艺、热/上电、贴装和 DFM 验证。

## 历史与完整性

本版继承 R6 提交 `321c03b45dece0b89f52a8f3d1d4b70550651624`。历史报告仅按其范围解读；旧覆盖数、旧电阻值或旧缺口不代表当前状态。

65 个工程变更文件及清单保持源字节。新 SVG 为原生 CAD 铜图，诊断 Gerber 为本项目导出；原始厂商 PDF/图片和运行时文件不上传。必要的上游 MIT 版权许可声明保留。

当前文件完整性以 `SHA256SUMS` 为准；逐版来源、排除项和检查点记录见 `PUBLICATION_PROVENANCE.json`。

## English summary

R7 adds ten conditional footprint assignments and excludes JP1/TP81/TP82 fabricated features from BOM, preserving all values, electrical bindings, on-board and DNP states. Coverage reaches 202 assigned / 52 unassigned. Fresh ERC and scoped geometry/population controls pass; the independent fixture retains three expected unrouted shared-net connections with no rule violations. Default paste export still includes two R528 apertures despite DNP. An explicit assembly/stencil variant remains mandatory before manufacturing. Full-board fit, routing and qualification remain open.
