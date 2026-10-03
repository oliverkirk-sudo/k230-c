# Historical pre-integration candidate note

Superseded in v7 by the conditional NVT4858 circuit in cad/integrated and the current root README. Fixed3.3V TF Default/High-Speed25/50MHz is the evidenced compatibility baseline. The text below records the earlier investigation and must not be read as current wiring status. See engineering/firmware/STORAGE_INTEGRATION_CONTRACT.md for the current firmware split.

# TF-only translation branch: architecture candidate, not wired

The discovered OTP boot-voltage dependency motivates investigation of a fixed1.8V MMC0 host/eMMC interface, with a dedicated translation stage only on the TF branch. It does not justify simply tying a3.3V card bus to a1.8V host.

NXP NVT4858 is a relevant candidate: the official manufacturer product/data-sheet descriptions specify1.08–1.98V host range,1.62–3.6V card-side range, auto-direction SD signaling and up to208MHz/SDR104 capability. This is a component capability, not proof the complete K230+TMUX+translator+carrier path meets timing. https://www.nxp.com/products/NVT4858 ; https://www.nxp.com/docs/en/data-sheet/NVT4858.pdf

Do not substitute NVT4857UK as a fresh design choice merely because a reference uses it: NXP's product page explicitly identifies that part as End of Life. The TI TXS02612 SDIO expander is another distinct part with different timing limits, not an unexamined substitute.

Before implementing NVT4858, verify exact pinout/package, power sequencing and disabled-state/backfeed limits, host/card pull resistors, CLK feedback route compatibility, propagation and setup/hold with the existing switch, and the card-side1.8/3.3V selection supply. Maintaining UHS modes requires intentional card-side signaling-voltage control and a BSP that keeps the physical host PHY consistent. A fixed3.3V TF branch must not be silently treated as supporting allUHS modes.

No new GPIO has been taken from the140-pin interface. The four reserved internal GPIOs currently serve two DVFS software buses. A voltage-control pin/alternative topology requires explicit internal resource and firmware allocation. No actual translator circuit or OTP configuration is included as approved in this checkpoint; no OTP has been generated or programmed. eMMC HS200 remains the target, not silently downgraded to HS52.
