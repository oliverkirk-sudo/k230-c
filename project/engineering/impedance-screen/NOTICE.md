# Calculator provenance and license

`calculate_screen.py` is licensed **GPL-2.0-or-later**, not under any MIT license associated with the original module repository. The complete GPL version 2 is included in [COPYING-GPL-2.0.txt](COPYING-GPL-2.0.txt). This notice does not relicense the original module or other repository content.

The `strip_centered` finite-copper branch expressions and `strip_offset` harmonic construction adapt the mathematics and branch structure of KiCad's publicly documented `STRIPLINE::lineImpedance` and `STRIPLINE::Analyse`. Because the implementation follows that source closely, it is treated as an adaptation rather than asserted to be a clean-room independent implementation. KiCad's source carries **Copyright The KiCad Developers** and GNU GPL version 2 or later. Original source: https://docs.kicad.org/doxygen/common_2transline__calculations_2stripline_8cpp_source.html (read 2026-09-30; displayed source lines 47–51 and 142–176).

The Hammerstad–Jensen and NI functions independently evaluate the published mathematical equations cited in `assumptions.json`, using new Python functions and names. Qucs' normalized-width implementation was consulted to interpret its mathematical documentation. The whole Python calculator is provided under GPL-2.0-or-later to preserve the KiCad-derived part's terms. No claim is made that these analytical equations constitute an electromagnetic field solver.

The report, input assumptions and numerical results are original task deliverables. Third-party document URLs remain references; no third-party manual or proprietary K230 model is redistributed here.
