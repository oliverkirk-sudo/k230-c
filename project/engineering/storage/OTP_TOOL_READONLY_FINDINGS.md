# Official OTP tool: read-only inspection

Observed2026-09-30 in the official live tool: https://www.kendryte.com/zh/tools/otp_config_generation_tool

SDIO0 I/O voltage exposes1.8V and3.3V choices. The page also exposes chip model, BootROM UART pinmux/voltage, OSPI voltage, and SDIO1 pinmux/voltage. Visible defaults are form defaults only; they do not report a connected chip, blank-silicon behavior, fuse readback, or earliest driven voltage.

The tool instructs users to confirm IO voltages against the actual board, configure OTP after assembly using the official burning tool, and warns that an incorrect setting can damage the chip and that OTP programming is irreversible. These establish a board-wide manufacturing prerequisite, not a safe automatically generated configuration.

No field value was changed, configuration file generated, account logged into, chip connected or OTP programmed. Any future OTP operation requires a separately reviewed full-board configuration and explicit approval. Do not generate it from untouched form defaults.

Before installing R528, obtain authoritative boot behavior/configuration evidence, verify the intended device's configuration/readback, and measure earliest relevant signals with isolation preserved. Other voltage fields must be checked against the selected carrier-bank supplies and BSP; checking SDIO0 alone is insufficient. The exact first-drive guarantee and0x91213410 producer/encoding remain unresolved.
