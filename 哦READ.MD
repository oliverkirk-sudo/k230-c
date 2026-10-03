# k230-c

## 当前检查点：R4 条件 BGA 身份与封装覆盖

在 R3 上，为 U1/U2/U3 增加三个原生 KiCad 工程候选封装绑定。**这是身份/条件几何检查点，不是生产版本；没有完整六层核心板 PCB，也没有 DDR 布线资格结论。**

当前入口：`project/cad/recovery-physical-candidate/CMK230_Core_REVIEW.kicad_pro`（原理图同名 `.kicad_sch`）。保持 `project/` 内相对目录结构。根说明文件保持 `哦READ.MD`。

## R4 变化与验证（2026-10-03）

- U1 K230：390 个物理焊盘；U2 Micron FW200：200 个；U3 Micron BH153：153 个，共 743 个。编号、坐标和有效引脚功能已核对，NC/DNU 物理球位保留
- 封装覆盖增至 158 个元件，尚有 96 个未分配；全部 254 个元件、1,509 个引脚绑定、电气值和装配属性保持不变，仅改变 U1/U2/U3 的封装字段
- 新 RAM 候选使用 0.30 mm NSMD 铜、0.40 mm 阻焊开口及独立 0.30 mm 锡膏孔。这些是工程假设，不是 Micron 制造焊盘推荐
- eMMC 最大本体图修正为 11.6 × 13.1 mm，工程 courtyard 为 12.1 × 13.6 mm；K230 增加 F.Fab 角点方向提示，A1 仍物理缺席。继承的 U1/U3 铜/阻焊/锡膏焊盘子树未改变
- 新 KiCad 9.0.2 ERC 为 0 错误、0 警告；孤立六层身份几何夹具 DRC 为 0。镜像、丢失 NC 球和错误行距负控按预期拒绝
- 独立审查的 30 项初查与 17 项图形修正检查通过；R528 仍默认 DNP，存储默认禁止

详细源证据、脚本、原生检查、独立审查及 34 个工程变更文件清单见 `project/recovery/r4-bga-coverage/`。源清单 SHA-256：`450519dc83316734587bd46b5425656dd6c5a6aadd23309b589068988f3e482b`。

## 必须保留的资格边界

- 孤立夹具为 66 × 32 mm、单焊盘独立测试网络；它不是 38 × 38 mm 核心板，也不证明整板容纳、互连、逃线、DDR 时序、阻抗或回流连续性
- 未导入任何历史八层 PCB、扇出、过孔或走线。六层数量本身不确定可制造的叠层；未选择 HDI 工艺
- 制造焊盘、铜蚀刻、阻焊对位、锡膏/钢网、焊球/焊点公差、贴装、via-in-pad、可靠性、高温/上电、DDR/PDN、DFM 和完整整板资格仍待关闭
- 仍需解决 96 个封装缺口，然后完成 38 × 38 mm、140 触点、1 mm 间距、恰好六个铜层、仅顶面贴装的完整布局布线
- R3 中的电感体下无关铜/孔限制与 R574 时钟偏置电气限制持续有效；普通 DRC 通过不能替代这些检查

## 版本与来源完整性

R4 继承 R3 提交 `d7fddd369ea61d5c2eb04578edda8813abab0e04`；R3 的六个被动器件绑定、验证和工程限制保留在 `project/recovery/r3-physical-coverage/`。恢复基线检查保留在 `validation/2026-10-03-restored/`，更早的缺库检查只是历史证据。其他历史报告按各自阶段和范围解读。

源 CAD、库、脚本、数据、网表、工程审查、来源 URL/哈希和必要的 `LICENSE-01studio.txt` 上游 MIT 版权许可声明保留。未为第三方材料新增授权，也未上传厂商 PDF/页面、图像或运行时缓存。部分历史生成输出仍按先前发布记录省略。

当前文件完整性以根目录 `SHA256SUMS` 为准；排除项、原始哈希和逐版增量见 `PUBLICATION_PROVENANCE.json`。R4 的 34 个源变更文件及其清单保持原始字节。

## English summary

R4 adds three conditional BGA bindings for U1/U2/U3 and verifies all 743 physical lands, reaching 158 assigned / 96 unassigned references. The 254-component / 1,509-binding circuit and population flags remain unchanged. Fresh ERC and isolated geometry DRC pass. Inherited U1/U3 pad subtrees remain unchanged after drawing-envelope/orientation corrections. Whole-board fit, six-layer routing, DDR/PDN and manufacturing qualification remain incomplete.
