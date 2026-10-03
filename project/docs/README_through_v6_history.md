# 当前检查点 v6（旧章节仅为历史过程）

v4 的 eMMC VDD/VDDF 供电含义反接已在 v5 修复；请勿使用 v4 接线或制板。当前 v6 保留此修复，并对131个存储器电源/地球位逐一回归。

当前内部工程14页、209个器件引用，另有19个不进BOM/PCB的可追溯电源声明。KiCad ERC为13错误+1警告。19个有来源的不用引脚处理和17条稳压器被动供电路径已有逐项依据；未给真实缺电网添加声明。

尚缺PMU冷启动/隔离释放策略、完整硬件复位/存储使能、OTP初始电压与TF转换方案、确切eMMC CReg参数，以及完整PCB与硬件验证。不能据此生产。详见 cad/integrated/README.md、engineering/erc-triage-v5.md 和 engineering/reset/SUPERVISOR_CANDIDATE_REVIEW.md。

以下内容保留过程记录，数字/测试版本以本节和 integrated 当前报告为准。

> v5供电纠正：请先阅读 `V5_CORRECTION_READ_FIRST.md`。旧v4的eMMC VDD/VDDF供电含义反接已修复；历史GUI截图不代表此修订。

# CM-K230 兼容核心板重新设计 · 内部电路评审草稿

日期：2026-09-30。配置基线：K230 + 1GB LPDDR4 + 16GB eMMC，TF/eMMC断电二选一。

优先打开 `cad/integrated/CMK230_Core_REVIEW.kicad_pro`：统一的多页内部候选原理图。原有接口/单独子电路保留作对照，不代表多个SoC。整体仍有明确未完成项，不可打样。

**这是包含已接线内部候选电路的评审工程。完整复位/存储启动策略、部分器件参数及PCB仍未完成。不可用于打样、采购下单或量产；没有Gerber、钻孔、贴片坐标或已布线PCB，也不声称整板ERC/DRC或硬件测试通过。**

## 已落实
- 38 × 38 mm 外形；140 个边缘接口，每侧 35 个，1 mm 节距；背面不装元器件
- 从 01Studio 原始符号提取 1–140 全部针脚；独立与官方底板示例 PDF 逐针比对，140/140 名称和编号一致
- 转换原厂底板配合焊盘，保留原始位置、尺寸、旋转；KiCad 9 载入确认 140 个焊盘
- 可编辑 KiCad 四分单元接口符号及接口合同原理图；成功导出 SVG，并检查排版
- 可编辑 38 × 38 mm PCB 轮廓，明确不含铜、孔、器件和布线

## 工程文件
- `cad/CMK230_Interface_ONLY.kicad_sch`：接口黑盒，不是内部电路；引脚电气类型统一为 passive，不能用于证明电源方向或 ERC 正确性
- `cad/CMK230.kicad_sym`：上述符号库
- `cad/CMK230.pretty/CMK230_Carrier_Mating_ONLY.kicad_mod`：**底板配合 SMD 焊盘**，不是核心板半孔封装
- `cad/CMK230_Module_Outline_ONLY.kicad_pcb`：只有 38 mm 方形轮廓；文件中默认两层/1.6mm设置只是EDA占位，未验证、未批准，不是本项目叠层或板厚规格
- `data/cm-k230-pinmap.csv/json`：逐针合同、原始证据位置及源文件哈希
- `data/mating_land_coordinates.csv`：底板焊盘坐标，以模块中心为原点；KiCad 正 Y 向下
- `docs/architecture.md`：系统结构、布局和电源策略
- `docs/release-gates.md`：进入原理图、布线和制板的必要条件及上电验证
- `data/candidate-bom.csv`：候选物料，绝非可采购 BOM
- `docs/sources.md`：来源、许可证边界、原始参考设计链接

## 关键事实与未解决事项
1. 原图背面无器件已由用户确认，外部 LPDDR4 必须与全部电源、去耦、eMMC 一起放在正面；无背面去耦会增加布局/供电完整性压力，不能只靠正面空间面积推断可布通
2. 图片 RAM 字样与 K230 支持的 LPDDR3/LPDDR4 体系存在冲突。不用照片猜测的 DDR3L 型号设计本板，改用官方验证过的 LPDDR4 候选
3. 候选 1GB RAM 为 Samsung K4F8E304HB-MGCJ（8Gb，双 x16 通道）；候选 eMMC 为 KLMAG1JETD-B041（16GB）；须锁定可采购完整后缀、温度级别与版本，并完成引脚/封装逐项审核
4. 引脚同名不代表电气兼容已成立。特别是 VOUT_3V3/1V8 的瞬态/保护能力（官网标注最大300mA/100mA），BANK0/1/2/3/4/5_VDDIO 的供电方向、是否内部固定或外部可选、以及 BOOT/RST 默认电平仍需确认
5. 原 PcbDoc 是无钻孔的 SMD 底板焊盘。它不能证明核心板半孔孔径、板厚、铜厚、金属化要求、铣边公差；这些必须从正式结构图/样品测量及板厂能力补齐
6. 改内部电路允许调整固件，但“原固件直接可用”尚未证明。内存训练、PMIC 控制、DVFS、启动选择、MMC 引脚复用、分区和接口测试均为交付的一部分

## 当前收敛点
已统一13页内部候选原理图，209个参考位号、1382个针脚记录。所有已分配网络与导出网表一致；最终ERC仍有51项（50错误、1警告），详见集成工程README及逐项报告。下一步是解决ROM前存储电压/开通、完整PG/复位、CReg数值及剩余引脚处置，完成器件/封装审核后再进行约束驱动PCB布局。

## 后续证据补充（仍为D0）
`engineering/`已加入124个模块功能到SoC球名候选、底板供电连接证据、23域电源预算、DDR封装长度冲突提示和TF/eMMC兼容调查。01Studio固件将eMMC配置在MMC0/1.8V/8bit/HS200；官方TF边缘接口也声明MMC0。原模块如何在两种装配中隔离或共享这些引脚未公开确认，这是进入完整内部网表前必须解决的存储接口问题。不能假定外部TF与eMMC同时可用，更不能将3.3V卡直接接入未确认的1.8V网络。

## KiCad实际测试
见`docs/KICAD_TEST_REPORT.md`及实际GUI截图。ERC139条未连接错误；空轮廓DRC0不能代表硬件通过。配合封装首次缺courtyard已修复，新增装配边界不改变140个焊盘。

## 二选一模式已获确认：新增隔离子电路
新增`cad/storage/`可编辑开关子电路及71项针脚网络表、4状态静态导通验证。默认eMMC、断电设置TF，11条路径隔离，不重定义外部GPIO。详见`engineering/storage/SELECTOR_DESIGN_CN.md`。原板隐藏共享拓扑不再是本隔离提案唯一前提，但BootROM首次驱动电压及硬件开通时序仍未确认；不得以软件后期开通替代ROM之前所需通路。

## 时钟/复位片段
新增`cad/core-aux/`，15器件37项连接通过导出一致性检查；片段ERC0/0。只有K230的7个系统球，不是完整SoC或核心板；晶体负载参数、启动和电源监控仍须完善。见`engineering/CORE_AUX_CN.md`。

## 最新组件表
`engineering/component-register.csv`列出集成草稿全部209个位号及候选值/DNP，`data/candidate-bom.csv`只是架构级概览。两者都不是可下单BOM；本工程没有已审核制造封装。
