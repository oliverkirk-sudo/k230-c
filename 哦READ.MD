# k230-c

## 当前检查点：R8 滤波磁珠与前馈电容条件焊盘

本版仅新增 13 个候选封装绑定：FB202–FB210 与 C202/C219/C224/C229。覆盖为 **215 个已分配、39 个未分配**。全部 254 个元件的其他属性、457 个网络、1,509 个引脚/功能/类型/网络绑定、BOM 和装配状态保持 R7 状态。仍无完整六层核心板，诊断 CAM 不是制造发布。

当前入口：`project/cad/recovery-physical-candidate/CMK230_Core_REVIEW.kicad_pro`（原理图同名 `.kicad_sch`）。保持 `project/` 内相对目录；根说明文件为 `哦READ.MD`。

## 本版范围与验证

- 九个磁珠绑定明确命名的 Murata BLM15PX121 18 µm 条件源图案；另保留 35/70 µm 独立封装选项。元件值和电气身份未改动，封装分配不自动批准最终采购 BOM
- 同一额定电流类别的铜宽随铜厚变化：18/35/70 µm 对应 1.2/0.7/0.5 mm。每块铜长 0.4 mm、中心 x=±0.4 mm；三种图案的独立阻焊开窗与锡膏孔均为名义 0.4 × 0.5 mm
- 绑定的 18 µm 选项为较大局部保留范围，**不代表已选定或批准工厂六层叠层**。精确名义阻焊模型没有加入铜/阻焊对位余量；工厂必须确认对位能力和实际工艺裕量
- 四个 1.2 nF 前馈位置采用 KEMET C0402C122J5GACTU 密度 B 源焊盘：0.62 mm 方形铜、中心 x=±0.45 mm、1.90 × 1.00 mm 源 courtyard。+0.05 mm 阻焊扩张及独立 1:1 锡膏仍为工程假设
- 原生导出复核确认 13 个 Footprint 字段和根版本标签外，原理图逐字节一致；全部非封装元件属性、完整网络和 DNP/BOM 状态保持不变。JP1/R45/R47/R528 保持 DNP
- 新 KiCad 9.0.2 ERC 为 0；20 × 13 mm 六层几何夹具 DRC 规则违规及未连接项均为 0。夹具使用独立诊断网络，不代表整板连接完成
- 原生保存/重载后的铜、阻焊、锡膏形状、尺寸和坐标与库及已保存 CAM 一致；三层各 8 个闪孔。八个独立负控通过，包括铜厚误选、肩部错误露铜/上锡、间距解释错误，以及原生物理间距违规

详细清单、来源 URL/哈希、原生结果和独立审查见 `project/recovery/r8-filter-feedforward-lands/`。原始增量 ZIP 与源清单身份记录在 `PUBLICATION_PROVENANCE.json`。

## 保留的工程门槛

局部矩形不证明后续走线截面积、散热或滤波能力。磁珠初始/试验后电阻限制不是热态 DCR 保证；实际峰值、浪涌、直流偏置下阻抗、滤波/谐振、时序和热仍须验证。FB206 仍须计入 R401 输入支路负载。

四个前馈电容保留原名义值，TI 方程与实际 10 kΩ 下分压电阻相符；这不建立全部负载/温度下环路稳定性。来源审查记录的 LCSC 最小/倍数 20 是数量偏好例外，仅为带日期的采购观察；未采购或锁定库存。

R7 的钢网门槛持续有效：**KiCad 默认 F.Paste 仍含 R528 的两个锡膏开口，DNP 与贴装/BOM 排除不等于钢网排除。** 制造前须明确装配/钢网版本，并检查实际锡膏输出；其余 DNP 元件也须遵守该策略。

39 个封装缺口为 36 个电容、2 个晶振反馈电阻和 RTC 晶体。仍须完成 38 × 38 mm/140 触点/1 mm 间距/恰好六铜层/仅顶面贴装的完整布局布线，以及 DDR/PDN、时钟、启动、热/上电、工艺与 DFM 验证。前版的寿命、精度、热电流和器件适用性限制继续有效。

## 历史与完整性

本版继承 R7 提交 `1fddab33bbd0a6d00e7c53c8f09ba6f72e5ada13`。89 个工程变更文件及清单保持最终公开源字节。来源阶段的私有路径工具已按公开子集记录排除；报告路径已规范化。新 SVG 与诊断 Gerber 为本项目原生导出；原始厂商 PDF/图片和运行时文件不上传，必要的上游 MIT 版权许可声明保留。

当前文件完整性以 `SHA256SUMS` 为准；逐版来源、排除项和检查点记录见 `PUBLICATION_PROVENANCE.json`。旧报告按其原范围和输入哈希解读，旧覆盖数或未分配状态不代表当前状态。

## English summary

R8 adds thirteen conditional ferrite/feedforward footprint assignments, reaching 215 assigned / 39 gaps. All other component identities, electrical bindings, BOM and population states are preserved. Fresh ERC, native geometry/CAM comparison and eight negative controls pass. The 18 µm ferrite reservation does not approve the factory copper stack; exact nominal mask openings lack registration allowance. Hot/bias/filter/loop/stencil conditions and complete-core routing remain open.
