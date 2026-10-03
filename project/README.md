# CM-K230 核心板重设计：v12 评审工程

最新说明：[V12_CORE_REVIEW.md](V12_CORE_REVIEW.md)

保留 38×38mm、140 针、1mm 间距、顶面器件、1GB LPDDR4、16GB eMMC，以及断电切换外部 TF。R528 默认 DNP，存储禁止；整板尚未完成布局布线、启动或高温资格验证。

## 打开哪些文件

- cad/high-temp-candidate/CMK230_Core_REVIEW.kicad_pro：当前条件式高温原理图，18 页、ERC0；同名 PCB 只是150个封装的部分导入，内部元件未放置
- cad/bga-engineering-candidates/bh153-sparse-trial/BH153_SPARSE_LOCAL_TRIAL.kicad_pcb：独立原生 eMMC 逃线试验，保留17个未连通项和32个悬空警告
- cad/conditional-process-check/：保留v11的38封装独立条件工艺规则试验，不是生产规则释放
- cad/edge-bound-seed/：140针逐一接入实际网络的边缘种子，尚无内部器件
- cad/castellation-proposal/：冻结的半孔和八层叠层机械提案，尚待工厂/装配联合接受
- cad/integrated/：保留 Samsung 参考分支及其原有温度限制

既有 GUI 截图按其实际版本保留；本轮 CLI、原生解析、故障对照和各阶段的限制见最新报告。几何局部通过、原理图 ERC0、整板可制造和硬件通过是不同结论。

历史说明保留在 V9_CORE_REVIEW.md、V10_CORE_REVIEW.md、V11_CORE_REVIEW.md 及 docs/。旧 v4 的 eMMC 电源映射错误已修复，禁止使用 v4 制板。
