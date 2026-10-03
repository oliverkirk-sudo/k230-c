# k230-c

## 当前检查点：R10 DNP 锡膏派生策略复核

本版新增独立的 DNP 锡膏派生工具及可复现测试，**所有既有工程文件保持 R9 原始字节**。电路版本仍为 RCV-R9，221 个封装已分配、33 个缺口；254 个元件、457 个网络、1,509 个引脚绑定、值、BOM 和装配状态未改变。

当前工程入口仍为 `project/cad/recovery-physical-candidate/CMK230_Core_REVIEW.kicad_pro`。新增工具入口为 `project/recovery/r10-dnp-paste-policy/README.md`；根说明文件保持 `哦READ.MD`。

## 已验证的限定结果

- 在 KiCad 9.0.2 上，默认导出和已测试的 DNP Fab 控制仍保留 DNP 锡膏；相关控制不等于锡膏过滤
- 新工具以固定哈希的原始板、master XML 和装配契约为输入，生成另名派生板。源板与派生板都必须通过精确封装身份、DNP/BOM/PnP、编号焊盘和 master 网络一致性检查
- 默认要求完整参考覆盖；孤立夹具必须显式启用 review-only 子集模式。缺失/未知编号、错误网络、不明锡膏归属或不支持的对象结构会停止，而不是猜测
- 只移除已确认 DNP 的锡膏层成员或符合条件的独立锡膏对象；所有非锡膏 token 保持不变。铜、阻焊、钻孔、位置和电气身份均保留；派生板不能覆盖原始设计
- 在精确 R9 输入上重新运行的合成夹具套件通过 42 项检查，包括 16 个预期拒绝负控。覆盖错误铜删除、拟装器件锡膏丢失、裸铜特征误加锡膏、DNP/网络/编号/位置异常和无归属锡膏
- 合成夹具的铜/阻焊/板框/Fab Gerber、钻孔和贴装输出在限定元数据归一化后保持一致。该夹具特意包含双面与重复焊盘测试构造，不改变核心板仅顶面贴装要求
- 实际恢复的 R7 十参考夹具通过另一项检查：先证明复制库文件与权威源文件哈希一致，再仅归一化十个封装库别名。**铜与阻焊各保持 18→18 个闪孔，锡膏 14→12，仅移除 R528 的两个开口**；其他非锡膏 CAM 层保持一致

独立别名复核、每对象派生记录、源文件哈希与诊断输出均随本版保存。负控文件故意无效，不得用于制造。

## 如何使用与尚未关闭的门槛

原始板继续作为规范设计，铜、阻焊、板框与钻孔应从原始板输出；仅从核验过的派生板导出对应装配版本的 F.Paste/B.Paste。源板、装配状态、库绑定或契约变化后，必须重新生成并检查派生结果。

R528 仍为 DNP 且不进入默认贴装文件；去掉锡膏不能代替禁止装配说明、电气禁止条件和硬件验证。本版解决的是所支持对象和已测试运行时内的限定导出策略，**未在完整核心板上应用，也没有钢网/装配工艺或生产资格**。钢网厚度、面积比、转移效率、锡膏、对位、回流及良率需另行验证。

R9 的有效电容量解释、热/偏压/老化、采购数量和工艺限制仍有效。33 个封装缺口为 30 个电容、2 个晶振反馈电阻和 RTC 晶体。38 × 38 mm/140 触点/1 mm 间距/恰好六铜层/仅顶面贴装的完整布局布线，以及 DDR/PDN、时钟、启动、热/上电与 DFM 仍待完成。

## 历史与完整性

本版继承 R9 提交 `45750f385a5261c139b819b4b333280d7c1acafb`。108 个新增工程文件及清单保持最终公开源字节；既有工程文件全部不变。路径已规范化；厂商原件、内部笔记、运行时缓存和日志不上传。诊断 Gerber 与故意损坏的负控板仅供复核，必要的上游 MIT 版权许可声明继续保留。

当前文件完整性以 `SHA256SUMS` 为准；逐版来源、排除项和检查点记录见 `PUBLICATION_PROVENANCE.json`。历史报告按其限定范围解读。

## English summary

R10 adds a review-only DNP paste derivation policy without changing any existing project file or the RCV-R9 circuit. The exact-copy 42-check suite passes, including 16 negative rejections. The recovered R7 fixture preserves copper/mask at 18 flashes each while paste falls from 14 to 12, removing only R528 apertures after hash-proven alias normalization. Strict source/derived pad-net and population parity remain mandatory. Full-board application and stencil/process qualification remain open; synthetic backside tests do not authorize backside core assembly.
