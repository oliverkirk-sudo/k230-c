# k230-c

## 当前检查点：R6 被动器件条件封装覆盖

本版仅为 25 个普通偏置电阻和 L21 增加 26 个候选封装绑定。**所有元件值、网络和装配属性保持 R5 状态；仍无完整六层核心板，也不是制造发布。**

当前入口：`project/cad/recovery-physical-candidate/CMK230_Core_REVIEW.kicad_pro`（原理图同名 `.kicad_sch`）。保持 `project/` 内相对目录；根说明文件为 `哦READ.MD`。

## 本版范围与验证

- 全部 254 个元件值、457 个网络、1,509 个引脚/功能/类型/网络绑定和装配属性不变；恰好 26 个 Footprint 字段改变
- 覆盖为 192 个已分配、62 个未分配。R45/R47/R528 保持 DNP；八个 DAT 上拉保持 R5 的条件 43 kΩ 值，R33 保持 270 kΩ，存储默认禁止
- 25 个普通偏置位置采用既有 CRCW0201 候选；未批量纳入精密 VSET、零欧/高电流或晶振反馈器件
- L21 保持 XFL4015-471MEB。推荐铜为两块 0.98 × 3.40 mm 矩形，中心距 2.37 mm、内间隙 1.39 mm；顶视图右侧 +X 的 pad 1 接 SW_CORE，左侧 pad 2 接 VDD0P8_CORE
- L21 最大本体 4.30 × 4.30 mm；工程 courtyard 为 4.80 × 4.80 mm。阻焊扩张 50 µm、独立 1:1 锡膏孔和 courtyard 均为待工厂验证的工程假设
- 新 KiCad 9.0.2 ERC 为 0；L21 独立六层几何夹具 DRC 为 0。抬高间距要求的负控按预期拒绝；镜像起始端、错接 SW/输出、改动 PG 电阻值和装上 DNP 的负控被检出
- 独立全图/几何复核及实际原生锡膏导出对比通过；全局锡膏覆盖参数的两种设置均保留实际 0.98 × 3.40 mm 独立开口

详细清单、来源哈希、原生结果和独立审查见 `project/recovery/r6-passive-coverage/`。56 个工程变更文件的源清单 SHA-256：`41e156fc71d4b10e1309578cfc231c354b290f847fc957d7bd48313e88f86145`。

## 保留的工程限制

L21 的数字引脚约定和装配方向提示不等于厂商标记尺寸。未将 Murata 特有的体下限制自动套用到 L21，但这也不批准任意体下走线；开关回路、回流、耦合和 EMI 仍需检查。L22–L26 的原有 Murata 限制持续有效。

偏置电阻的电气/热屏估不证明实际膜温、瞬态、CORE PG→EN 噪声/斜率、I²C 漏电/RC、复位/PMU/启动时序或存储空闲电平。订货代码不代表现货、生命周期或任务寿命资格。

独立 10 × 10 mm 夹具无完整路线或平面；其通过不等于整板、电源回路或制造通过。仍须完成 62 个封装缺口、38 × 38 mm/140 触点/1 mm 间距/恰好六铜层/仅顶面贴装的完整布局布线，以及 DDR/PDN、工艺、热/上电、贴装和 DFM 验证。

## 历史与完整性

本版继承 R5 提交 `a9618b50c6e97cfe833c88841b2a73f225e403a9`。R3–R5 的限定结论和未关闭条件仍有效。R6 内的历史偏置审查通过明确的不变图桥接使用，旧的假设覆盖数或 47 kΩ DAT 提示不能当作当前 R6 状态。

56 个工程变更文件及清单保持原始字节。三个新 SVG 已检查，分别为自制解释图和原生 CAM 对照图，不是厂商页面；原始厂商 PDF/图片和运行时文件不上传。必要的上游 MIT 版权许可声明保留。

当前文件完整性以 `SHA256SUMS` 为准；逐版来源、排除项和检查点记录见 `PUBLICATION_PROVENANCE.json`。旧报告仅按其原有范围解读。

## English summary

R6 adds 26 conditional footprint assignments without changing values, nets or population attributes. Coverage reaches 192 assigned / 62 unassigned references. Fresh ERC and isolated L21 geometry DRC pass; independent graph, geometry and actual paste-export controls pass. L21's marked right-hand start terminal remains on SW_CORE. Full-board fit/routing, switching-loop behavior, thermal and manufacturing qualification remain open.
