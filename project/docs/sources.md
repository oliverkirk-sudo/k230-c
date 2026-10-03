# 来源与授权边界

## 01Studio接口依据
原仓库：https://github.com/01studio-lab/CanMV-K230/tree/main/hardware/CM-K230
冻结提交：a27732a8c02171a71b61a1eec8671b7118cc4926
本包 `source-interface/` 保留原接口SchDoc/PcbDoc，配套MIT许可证见 `LICENSE-01studio.txt`；转换物保留来源。原始两页底板示例PDF用于独立逐针对照，证据位置/哈希见pinmap JSON。用户照片仅作外观参考，不能建立内部连线或完整器件料号。

## Canaan芯片与参考实现
硬件指南：https://github.com/kendryte/k230_docs/blob/main/en/00_hardware/K230_Hardware_Design_Guide.md
LP4参考文件目录：https://github.com/kendryte/k230_docs/tree/main/zh/00_hardware/K230_LP4
- 已取得LP4 Cadence DSN、PCB ZIP、BOM XLSX用于研究；本交付不冒充这些文件是38mm核心板设计
- EVB BOM含两个泛化LP4器件条目与4GB eMMC，与本项目1GB+16GB配置不同，不能直接照抄采购
CanMV示例原理图：https://github.com/kendryte/k230_docs/blob/main/zh/00_hardware/CanMV_K230/CanMV-K230-V1.0_2023-09-15.pdf
DDR软件适配：https://github.com/kendryte/k230_docs/blob/main/zh/01_software/board/osdrv/K230_lpddr4_lpddr3驱动适配指南.md
引脚表索引：https://github.com/kendryte/k230_docs/blob/main/README.md

Canaan仓库根LICENSE为BSD-2-Clause风格许可，但硬件指南另含版权声明；不能把根软件许可自动解读为所有芯片文档/制造数据的无限再分发权。本包主要保留链接及原创设计评审，不分发Canaan原始文档和CAD。

## 器件数据表
Samsung LPDDR4（制造商编写，第三方公开镜像；已读取PDF正文）
https://www.szyuda88.com/home/8/a/2lhtb2/resource/2021/05/26/60ade38424a32.pdf
K4F8E304HB-MGCJ：8Gb，2通道×16，200FBGA，10×15mm，VDD1/VDD2/VDDQ=1.8/1.1/1.1V；确认页7–8。器件采购、生命周期及封装最终审核尚未完成。

Samsung eMMC（制造商编写，第三方公开镜像；已读取PDF正文）
https://datasheet.lcsc.com/lcsc/2007011825_Samsung-KLMAG1JETD-B041_C499919.pdf
KLMAG1JETD-B041：16GB，153FBGA，11.5×13×0.8mm；VCC2.7–3.6V，VCCQ1.7–1.95V或2.7–3.6V；确认页4。主控仍按HS200设计。

EA3059（制造商编写，第三方公开镜像；风险审查依据）
https://xonstorage.z8.web.core.windows.net/pdf/everanalog_ea3059_apr22_xonlink.pdf
不纳入冻结BOM；连续/峰值和EN门限不能混用。

## 证据等级
接口编号/名称：原始CAD＋PDF二次验证。
候选RAM：Canaan验证型号列表＋Samsung数据表。
候选eMMC：Samsung数据表，非当前采购可得性证明。
内部电气兼容、PMIC最终选型、叠层/孔径、满频/温度可靠性：未验证。
