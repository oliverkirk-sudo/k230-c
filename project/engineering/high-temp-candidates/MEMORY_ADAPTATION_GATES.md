# Memory variant acceptance gates

This record concerns the conditional Micron core only. It does not endorse rewriting a Samsung board's firmware or changing OTP.

## LPDDR4

The200-ball dual-channel single-rank map has the same active physical positions after explicit rank0/channel-name aliases. This permits reuse of the source65-net correspondence as a **candidate topology**, not reuse of unexamined electrical timing. The five changed DNU→NC balls stay isolated. A5ZQ0 uses240Ω±1% toVDDQ per Micron's pin description.

Micron's MR4 Table33 says higher reported temperature requires reduced tREFI/tREFIpb/tREFW intervals; code110 additionally requests timing derating. The1x baseline corresponds to85°C, while0.5x/0.25x denote shorter intervals. AAT's105°C case rating is conditional on observing its temperature-dependent requirements. Handle out-of-range codes as a fault, not as ordinary operation. Do not infer that on-chip self-refresh management automatically updates the host controller's active-mode refresh.

Acceptance must cover actual selected density/rank, CA/DQ mapping, ODT/drive/VREF, clock/latencies, ZQ calibration, reset/power timing, MR4 handling, training at cold/hot corners and memory stress. No controller binary compatibility has been demonstrated.

## eMMC

Micron'sTable13 gives its own pull/bypass/CReg network. Existing CMD22k, DAT47k andRST10k fit its nominal ranges. H5DS receives a separate47k bias while the host's unused strobe remains separately biased. The localCReg andVCC/VCCQ bypass quantities have been drawn, but no actual MPN effective-capacitance or hot-corner qualification is implied.

Preserve allVSS/VSSQ balls and separateVCC fromVCCQ. VSF signals are internally functional; leave the seven positions unused and never infer permission to ground or repurpose them. Confirm reset-enable configuration, power-fail behavior and device timing in the selected image. No factory programming or irreversible bit update has been performed.

Sources are the manufacturer-authored PDFs linked in thermal-candidate-sources.json: Micron automotive200-ball LPDDR4/LPDDR4X RevF10/2020 and automotive eMMC RevG10/2018. Raw proprietary PDFs are not distributed in this project; only derived pin/requirement facts are included. Exact part lifecycle/sourcing remains unqualified.
