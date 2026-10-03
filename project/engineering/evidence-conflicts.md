# 证据冲突与连接矩阵状态

## 模块到SoC
`module-to-soc-candidates.csv`有140行，124行填有球名，16行是供电/地等不能对应单一球的空白。它是功能名对应候选，**不证明原模块内部直连**。每行有状态与来源；任何串阻、隔离、滤波、互斥选择均需另行设计验证。

TFCARD原先仅凭CanMV通用板无法确定，后查到01Studio官方PinOUT文字表宣称TFCARD17–22是MMC0。结合Canaan U1.4原理图得到候选：17D5、18C5、19B5、20C6、21A5、22D6。不可将它们绑到GPIO54–59/MMC1。内部eMMC也需要MMC0，二者同时使用/隔离/切换尚不能从文字表证明。

## 官网文字表与图形不一致
来源：https://wiki.01studio.cc/en/docs/canmv_k230/intro/canmv_k230/#pinout
图形：https://wiki.01studio.cc/en/assets/images/CM-K230_4-f7197fa1781a2c7207140b371b519181.png

已查看原图像；140针原始CAD与底板PDF一致。官网文字表存在：
- 55/56音频左右输出互换；本稿继续按CAD/图形55=HP_OUTR、56=HP_OUTL
- 119文字GPIO23，但CAD/图形BANK0_GPIO13
- 66–70文字若干CSI2，图形为CSI0
- GPIO6文字JTAG别名与Canaan信号定义不一致

这些冲突说明不能以网页文字自动生成全板网表。TFCARD的MMC0功能目前依官方文字声明，并单列验证门槛。

## DDR源表风险
`ddr-package-length-reference.csv`包含73条封装内线长记录。官方指南将B18/A18与B15/A15两组DQS同时写成DQSB1P/N别名；该表不能单独定义LP4接线。原名原数保留并标记冲突；不得凭推测把其中一组改成DQSB0后直接布板。已进一步查看官方指南Figure3-12实际原理图，B18/A18明确为DQS0_T/C_B，B15/A15为DQS1_T/C_B；记录在新增65信号端点候选中。但文字表原始错别名仍保留，不能自动用别名连网。

## 实际底板连接证据
六个BANKn_VDDIO连接底板3V3网，pin7 VOUT_3V3也标在同网；这支持底板正常使用3.3V bank的要求。底板另有名为3V3-EXT的稳压网，不与3V3混同。当前仍不把底板接法视为原模块内部电源方向、最大容性负载或时序的完整证明。
