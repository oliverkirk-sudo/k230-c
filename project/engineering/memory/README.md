# 内存/存储球图提取（不是完成网表）

RAM：依据Samsung K4F8E304HB-MGCJ数据表第10页。已查看实际渲染图像；原图标注Top View。CSV有264个网格位置，64个NB无球，200个实体球；保留DNU与NC差异。不能将NB生成焊盘，DNU不得擅自接地。数据表第9页外形图另有Bottom View，制作封装时必须保持A1、镜像方向和非均匀间距正确；此表尚不包含封装XY坐标。

RAM球图统计：68信号、58地、52电源、17DNU、5NC、64NB。此表只回答器件各球是什么，不决定其接哪一个K230球。DQSB文字别名冲突已由官方Figure3-12原理图澄清，但实际DDR交换/训练仍需固件验证，不生成假完整DDR网表。

 eMMC：依据Samsung KLMxGxJETD-B041第5页，原图标注“Ball-side down view”。33个功能/供电脚来自明确文字表；完整196网格/153实体球表以同页实际球图手工补齐NC/RFU与无球位置，**仍待独立逐位置复核**，不可直接作为制造封装。NC、RFU、NO_BALL不能混为同一含义。

`emmc-function-endpoint-candidates.csv`是11个MMC0数据/时钟/命令/复位端点对照。它没有决定外部TF共享/隔离，也不是保证可运行的连接清单。Data Strobe未在该HS200候选表中强行连线；最终按K230参考实现及eMMC数据表审查。eMMC C2 VDDI为内部稳压稳定节点，不是可随意接外部1.8V的电源输入，外接电容规则待最终应用电路核对。

所有原始资料链接见docs/sources.md；PDF哈希见data/research-source-hashes.json。原PDF不随包分发。当前文件未形成电气规则合格的K230/DRAM/eMMC完整原理图，也没有进行SI/PI或实板验证。

## 65条DDR端点候选
`ddr-reference-adaptation-candidates.csv`按官方Figure3-12逐项记录K230连接的逻辑DQ/CA/CK/DQS/DMI/CS/CKE/RESET，并对应至所选Samsung双通道器件球名。65个两端球各自唯一；这是按功能将两颗单通道参考设计改为一颗双通道器件的提案，未验证训练初始化或布线。没有给出完整电源、终端、校准/ODT、去耦和NC规则，不能直接制板。
原始两幅官方图：https://raw.githubusercontent.com/kendryte/k230_docs/main/zh/00_hardware/images/HDG/image023.png 与image026.png（同目录）。已检查图像，不从错别名表推导。

## 后续eMMC核验已完成
已直接从制造商PDF第5页提取153个圆形球位和46个文本标签，并与手工表逐位置比对：107个NC、13个RFU、33个功能球全部一致，196网格位置完全匹配。N12在PDF中重复画了同一圆形，按完全相同坐标去重。详见emmc-grid-verification.json。集成工程据此标记制造商要求不连接的端点，其他未知网络没有用NC掩盖。
