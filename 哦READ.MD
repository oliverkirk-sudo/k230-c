# k230-c

## 当前检查点：R9 eMMC 旁路电容条件焊盘

本版为 C64/C65/C69/C70/C71/C72 增加六个候选封装绑定，覆盖为 **221 个已分配、33 个未分配**。全部 254 个元件值及其他非封装属性、457 个网络、1,509 个引脚/功能/类型/网络绑定、BOM 和装配状态保持 R8 状态。仍无完整六层核心板，诊断 CAM 不是制造发布。

当前入口：`project/cad/recovery-physical-candidate/CMK230_Core_REVIEW.kicad_pro`（原理图同名 `.kicad_sch`）。保持 `project/` 内相对目录；根说明文件为 `哦READ.MD`。

## 本版范围与验证

- C64/C65 保持连接 EMMC_VDDIM，即 U3.C2 的内部稳压器电容节点；C69/C70 保持 VEMMC_IO；C71/C72 保持 VDD_3V3。六个 pin 2 均为 GND。VDDIM 不能当作 VCCQ，也不能由外部电源驱动
- C64/C69/C71 使用 Murata GRM188R71A225KE15D 候选：2.2 µF、±10%、10 V、X7R、0603。铜为 0.65 × 0.70 mm，中心 x=±0.675 mm，内隙 0.70 mm；属于源回流范围内的中点工程选择，不是厂商唯一规定图案
- C65/C70/C72 使用 GRM155R71C104KA88D 候选：100 nF、±10%、16 V、X7R、0402。铜为 0.40 × 0.50 mm，中心 x=±0.40 mm，内隙 0.40 mm
- 两种最大本体分别为 1.70 × 0.90 mm 与 1.05 × 0.55 mm；工程 courtyard 为 2.60 × 1.50 mm 与 1.80 × 1.20 mm。+0.05 mm 阻焊扩张、独立 1:1 锡膏及 courtyard 均须工厂接受
- 独立完整原理图结构比较仅允许六个 Footprint 字段和根 RCV-R9 版本标签变化；BOM CSV 保持字节一致。JP1/R45/R47/R528 保持 DNP，默认存储资格仍为禁止状态
- 新 KiCad 9.0.2 ERC 为 0；20 × 13 mm 六层孤立几何夹具 DRC 规则违规及未连接项均为 0。原生保存/导出铜、阻焊、锡膏的尺寸与坐标通过复核，每层 4 个闪孔
- 七个独立负控通过：三种电容电源节点混接、未授权名义值变化、DNP 变化、错误焊盘尺寸，以及保存后实际 0.10 mm 铜间距对 0.20 mm 规则的 DRC 拒绝

详细清单、来源 URL/哈希、原生结果和独立审查见 `project/recovery/r9-emmc-bypass-lands/`。源清单与原始增量 ZIP 身份记录在 `PUBLICATION_PROVENANCE.json`。

## 电容量与制造资格仍待确认

Micron Table 13 列出电容 Min/Max/Typ，但未明确其有效电容量的偏压、温度、容差及老化条件。当前保留的名义值符合表中数字，不能因此宣称实际热态/偏压/老化裕量已保证；把各列直接当作绝对有效值下限也属于尚未证实的解释，不能据此断言 Micron 违规。

不得由 VCCQ 推断 VDDIM 的数值电压。来源审查未建立该电压范围；未来若需改变名义电容量，应另做一致的电气修订。本版没有改变名义值。

厂商当前批准图、生命周期、采购数量及实际工厂接受仍开放。已找到 JLC 目录身份，MOQ1 尚未验证；没有采购或锁定库存。两器件的额定温度范围不等于整机或有效电容量已完成热资格。

前版门槛持续有效：磁珠铜厚、零阻焊对位余量、后续铜截面积和热/偏置滤波仍需验证；**R528 默认锡膏导出仍含两个开口，DNP 或 BOM/PnP 排除不等于钢网排除**。制造前必须明确装配/钢网版本并检查实际输出。

33 个封装缺口为 30 个电容、2 个晶振反馈电阻和 RTC 晶体。仍須完成 38 × 38 mm/140 触点/1 mm 间距/恰好六铜层/仅顶面贴装的完整布局布线，以及 BGA 邻近去耦、DDR/PDN、时钟、启动、热/上电、工艺与 DFM 验证。孤立夹具不代表整板连接或局部 BGA 旁路放置已完成。

## 历史与完整性

本版继承 R8 提交 `f5181cb06de490fb23de0e79c619210a664b3212`。52 个工程变更文件及清单保持最终公开源字节。报告路径已规范化；新 SVG 与诊断 Gerber 为本项目原生导出。原始厂商 PDF/图片和运行时文件不上传，必要的上游 MIT 版权许可声明保留。

当前文件完整性以 `SHA256SUMS` 为准；逐版来源、排除项和检查点记录见 `PUBLICATION_PROVENANCE.json`。历史报告按其原范围和输入哈希解读。

## English summary

R9 adds six conditional eMMC bypass footprint assignments, reaching 221 assigned / 33 gaps. All other component attributes, values, complete electrical bindings, BOM and population states are preserved. Fresh ERC, isolated geometry DRC, source/native CAM comparison and seven negative controls pass. Micron Table 13's nominal/effective interpretation, combined temperature/bias/aging capacitance, procurement quantities and manufacturing process remain open. This is not a complete core layout or production release.
