# k230-c

## 当前检查点：R3 条件封装覆盖

在已恢复并核验的 v12 + R2.1 源工程上，本版为 L22–L26 和 R574 增加六个候选封装绑定。**这是原理图/候选封装检查点，不是生产版本；当前候选仍没有完整六层核心板 PCB。**

当前入口：`project/cad/recovery-physical-candidate/CMK230_Core_REVIEW.kicad_pro`（原理图同名 `.kicad_sch`）。保持 `project/` 内相对目录结构。

## R3 变化与验证（2026-10-03）

- L22/L23 绑定现有 Murata DFE201612E-R24M=P2 候选；L24/L25/L26 绑定 DFE201610E-R47M=P2 候选
- R574 绑定新建 Vishay CRCW0201 来源核对焊盘候选；电气值、引脚功能、网络和 DNP 不变
- 封装覆盖由 149 增至 155 个元件，尚有 99 个未分配；L21 仍未分配
- 全部 254 个元件和 1,509 个引脚绑定保持一致，只有上述六个封装字段改变；R528 仍默认 DNP，存储默认禁止
- KiCad 9.0.2 新 ERC：0 错误、0 警告。R574 独立六层几何夹具 DRC 为 0；提高间距要求的负控按预期拒绝
- 错误封装、移除 DNP、改值、错误时钟偏置网络均被负控检出。原理图验证与夹具检查不代表整板通过

详细结果、可重跑脚本、27 个变更文件的源哈希和独立几何审查见 `project/recovery/r3-physical-coverage/`。R3 源清单 SHA-256：`73eaddc8f8b261d1affe5c2291bbb92fcdbe4e234e270a22b1858ac4e41e9310`。

## 尚未关闭的工程限制

- 38 × 38 mm、140 触点、1 mm 间距、恰好六个铜层及仅顶面贴装仍是设计要求；尚无当前整板布局布线或制造验收
- Murata 电感体下的无关铜、过孔和孔限制必须在实际位置、旋转和所有相关层明确检查。图纸标记不强制执行，普通 DRC 通过也不能替代此检查
- R574 铜焊盘来源已核对，但阻焊、钢网、装配、局部走线、泄漏、馈通、部分上电和时序仍待资格验证
- 其他未分配封装、DDR/时序、高温/上电、PDN、DFM、采购型号和工厂工艺仍需逐项关闭
- 历史八层试验、隔离几何夹具和负控板仅供追溯，不能当作当前六层成品；BGA 身份一致也不等于制造封装或逃线合格

## 恢复基线与历史证据

R3 继承已发布提交 `4362d103cb08000e34799f01544baf3daca0bb2f`，没有重写历史。恢复基线的重新检查保留在 `validation/2026-10-03-restored/`；更早缺少 v12 时的 150 条缺库警告保留在 `validation/2026-10-03-delta-only/`，已由完整恢复后的 0/0 结果取代。

- v12 ZIP SHA-256：`63dab93b8433b3a367571ec64b11568b9c81dc466e8d562ce2108b647d341e58`
- R2.1 ZIP SHA-256：`4e23cf611b37900dab169f0b44da5974ae70c65bbcf7624c97ccb16688eb3b5b`

`project/` 中其他历史报告仍按各自阶段和范围解读，不代表全部在本版重跑。

## 来源与发布完整性

源 CAD、库、脚本、数据、网表、工程审查、来源 URL/哈希和必要的 `LICENSE-01studio.txt` 上游 MIT 版权许可声明均保留。未为第三方材料新增授权。厂商 PDF/扫描页面、图像、运行时缓存、会话设置、日志、备份 ZIP 和部分大型历史搜索生成结果未上传；需要省略输出的旧检查须先重新生成。

当前发布文件完整性以根目录 `SHA256SUMS` 为准；恢复检查点的排除项、原始哈希及 R3 增量记录见 `PUBLICATION_PROVENANCE.json`。R3 的 27 个源变更文件及其清单按原始字节保存。

## English summary

R3 adds six conditional footprint bindings (L22–L26 and R574), increasing coverage to 155 assigned / 99 unassigned references. All 254 components, 1,509 pin bindings, values and population flags remain unchanged. Fresh ERC and the isolated geometry fixture pass; negative controls detect the intended errors. This is not a production release: active full-board six-layer layout/routing and manufacturing, thermal and timing qualification remain incomplete.
