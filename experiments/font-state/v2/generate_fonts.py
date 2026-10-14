from __future__ import annotations

from pathlib import Path
from fontTools.fontBuilder import FontBuilder
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.feaLib.builder import addOpenTypeFeaturesFromString
from fontTools.ttLib import TTFont

UPM = 1000
OUT = Path(__file__).resolve().parent / "generated"
OUT.mkdir(exist_ok=True)

ASCII = [chr(i) for i in range(32, 127)]

def gname(ch: str) -> str:
    if ch == ' ':
        return 'space'
    if ch.isalnum():
        return ch
    return 'u%04X' % ord(ch)


def box_glyph(width: int, inset: int = 90):
    pen = TTGlyphPen(None)
    if width > inset * 2:
        x0 = inset
        x1 = min(30000, max(inset + 20, width - inset))
        y0, y1 = 120, 720
        # Simple outline box; intentionally generic. Geometry, not legibility, is the point.
        pen.moveTo((x0, y0)); pen.lineTo((x1, y0)); pen.lineTo((x1, y1)); pen.lineTo((x0, y1)); pen.closePath()
        ix0, ix1 = x0 + 55, x1 - 55
        iy0, iy1 = y0 + 55, y1 - 55
        if ix1 > ix0 and iy1 > iy0:
            pen.moveTo((ix0, iy0)); pen.lineTo((ix0, iy1)); pen.lineTo((ix1, iy1)); pen.lineTo((ix1, iy0)); pen.closePath()
    return pen.glyph()


def empty_glyph():
    return TTGlyphPen(None).glyph()


def build_font(family: str, filename: str, widths: dict[str, int], cmap: dict[int, str], features: str = ''):
    glyph_order = ['.notdef'] + list(dict.fromkeys(list(cmap.values()) + list(widths.keys())))
    glyphs = {'.notdef': box_glyph(UPM)}
    metrics = {'.notdef': (UPM, 0)}
    for name in glyph_order[1:]:
        w = int(widths.get(name, UPM))
        metrics[name] = (w, 0)
        glyphs[name] = empty_glyph() if name == 'space' or w == 0 else box_glyph(w)

    fb = FontBuilder(UPM, isTTF=True)
    fb.setupGlyphOrder(glyph_order)
    fb.setupCharacterMap(cmap)
    fb.setupGlyf(glyphs)
    fb.setupHorizontalMetrics(metrics)
    fb.setupHorizontalHeader(ascent=800, descent=-200, lineGap=0)
    fb.setupNameTable({
        'familyName': family,
        'styleName': 'Regular',
        'uniqueFontIdentifier': family + ' Regular 1.0',
        'fullName': family + ' Regular',
        'psName': family.replace(' ', '') + '-Regular',
        'version': 'Version 1.0',
    })
    fb.setupOS2(
        sTypoAscender=800,
        sTypoDescender=-200,
        sTypoLineGap=0,
        usWinAscent=800,
        usWinDescent=200,
    )
    fb.setupPost()
    fb.setupMaxp()
    font = fb.font
    if features.strip():
        addOpenTypeFeaturesFromString(font, features)

    ttf = OUT / f'{filename}.ttf'
    font.save(ttf)

    # Also emit WOFF2 for the browser harness.
    wf = TTFont(ttf)
    wf.flavor = 'woff2'
    woff2 = OUT / f'{filename}.woff2'
    wf.save(woff2)
    return ttf, woff2


def ascii_cmap():
    return {ord(ch): gname(ch) for ch in ASCII}


def metric_font():
    cmap = ascii_cmap()
    widths = {name: UPM for name in cmap.values()}
    widths['space'] = UPM
    return build_font('Probe Metric', 'ProbeMetric', widths, cmap)


def token_font():
    cmap = ascii_cmap()
    widths = {name: UPM for name in cmap.values()}
    widths['space'] = UPM
    token_widths = {
        'tok.ALICE': 8000,
        'tok.BOB': 12000,
        'tok.CAROL': 16000,
        'tok.DAVE': 20000,
    }
    widths.update(token_widths)
    features = '''
    languagesystem DFLT dflt;
    feature liga {
      sub A L I C E by tok.ALICE;
      sub B O B by tok.BOB;
      sub C A R O L by tok.CAROL;
      sub D A V E by tok.DAVE;
    } liga;
    '''
    return build_font('Probe Token', 'ProbeToken', widths, cmap, features)


def contextual_font():
    # Bounded alphabet A/B/C, max 3 payload characters, introduced by ^.
    # Each position contributes a base-4 digit to total advance:
    #   payload code units use 0.5em * base-4 weights.
    #   A/B/C digits are 1/2/3; position weights are 1/4/16.
    #   '^' contributes a fixed 2em sentinel.
    # Therefore total advance is injective for ^[ABC]{1,3}, while every glyph stays < 32768 font units.
    cmap = ascii_cmap()
    widths = {name: UPM for name in cmap.values()}
    widths[gname('^')] = 2000
    for pos, weight in [(1, 1), (2, 4), (3, 16)]:
        for digit, ch in enumerate('ABC', start=1):
            widths[f'{ch}.p{pos}'] = digit * weight * 500

    features = '''
    languagesystem DFLT dflt;
    @P1 = [A.p1 B.p1 C.p1];
    @P2 = [A.p2 B.p2 C.p2];
    feature calt {
      lookup Pos1 {
        sub u005E A' by A.p1;
        sub u005E B' by B.p1;
        sub u005E C' by C.p1;
      } Pos1;
      lookup Pos2 {
        sub @P1 A' by A.p2;
        sub @P1 B' by B.p2;
        sub @P1 C' by C.p2;
      } Pos2;
      lookup Pos3 {
        sub @P2 A' by A.p3;
        sub @P2 B' by B.p3;
        sub @P2 C' by C.p3;
      } Pos3;
    } calt;
    '''
    return build_font('Probe Context', 'ProbeContext', widths, cmap, features)


def main():
    outputs = []
    outputs.extend(metric_font())
    outputs.extend(token_font())
    outputs.extend(contextual_font())
    for p in outputs:
        print(p.relative_to(Path(__file__).resolve().parent))

# Additional v2 experiments appended below; retaining v1 font generators unchanged.
from fontTools.ttLib import newTable
from fontTools.ttLib.tables._f_v_a_r import Axis
from fontTools.varLib.featureVars import addFeatureVariations


def token_context_font():
    """Same ligatures moved into calt; compare with liga in editable controls."""
    cmap = ascii_cmap()
    widths = {name: UPM for name in cmap.values()}
    widths.update({'tok.ALICE': 8000, 'tok.BOB': 12000, 'tok.CAROL': 16000, 'tok.DAVE': 20000})
    features = '''
    languagesystem DFLT dflt;
    feature calt {
      sub A L I C E by tok.ALICE;
      sub B O B by tok.BOB;
      sub C A R O L by tok.CAROL;
      sub D A V E by tok.DAVE;
    } calt;
    '''
    return build_font('Probe Token Context', 'ProbeTokenContext', widths, cmap, features)


def address_variable_font():
    """GSUB calt creates positional glyphs, rclt FeatureVariations gates by ADDR axis.

    String ^ABC; axis ADDR=1 emits 1em sentinel + 4em for A, ADDR=2
    emits 1em + 8em for B, ADDR=3 emits 1em + 12em for C.
    This is a selected-symbol geometry oracle, not arbitrary textarea addressing.
    """
    cmap = ascii_cmap()
    widths = {name: UPM for name in cmap.values()}
    widths[gname('^')] = 1000
    for pos in (1, 2, 3):
        for digit, ch in enumerate('ABC', start=1):
            widths[f'{ch}.p{pos}'] = 1000
            widths[f'{ch}.p{pos}.off'] = 0
            widths[f'{ch}.p{pos}.on'] = digit * 4000
    features = '''
    languagesystem DFLT dflt;
    @P1 = [A.p1 B.p1 C.p1];
    @P2 = [A.p2 B.p2 C.p2];
    feature calt {
      lookup Pos1 {
        sub u005E A' by A.p1;
        sub u005E B' by B.p1;
        sub u005E C' by C.p1;
      } Pos1;
      lookup Pos2 {
        sub @P1 A' by A.p2;
        sub @P1 B' by B.p2;
        sub @P1 C' by C.p2;
      } Pos2;
      lookup Pos3 {
        sub @P2 A' by A.p3;
        sub @P2 B' by B.p3;
        sub @P2 C' by C.p3;
      } Pos3;
    } calt;
    feature rclt {
      sub space by space;
    } rclt;
    '''
    ttf, _ = build_font('Probe Address', 'ProbeAddress', widths, cmap, features)
    font = TTFont(ttf)
    var = newTable('fvar')
    axis = Axis()
    axis.axisTag = 'ADDR'
    axis.minValue = 0.0
    axis.defaultValue = 0.0
    axis.maxValue = 3.0
    axis.flags = 0
    axis.axisNameID = font['name'].addName('Address', platforms=((3, 1, 0x409),))
    var.axes = [axis]
    var.instances = []
    font['fvar'] = var
    conditions=[]
    # Values are normalized against default=0, maximum=3.
    # Non-overlapping bands tolerate rounding when a scroll-linked animation
    # arrives slightly off an integral ADDR value.
    for address, lo, hi in ((1, 0.25, 0.42), (2, 0.58, 0.75), (3, 0.90, 1.0)):
        remap={}
        for pos in (1,2,3):
            for ch in 'ABC':
                remap[f'{ch}.p{pos}']=f'{ch}.p{pos}.on' if pos==address else f'{ch}.p{pos}.off'
        conditions.append(([{'ADDR':(lo,hi)}], remap))
    addFeatureVariations(font, conditions, featureTag='rclt')
    font.save(ttf)
    wf=TTFont(ttf)
    wf.flavor='woff2'
    woff2=OUT/'ProbeAddress.woff2'
    wf.save(woff2)
    return ttf, woff2

if __name__ == '__main__':
    main()
    # Emit the v2 probe fonts as part of the same reproducible build.
    for paths in (token_context_font(), address_variable_font()):
        for path in paths:
            print(path.relative_to(Path(__file__).resolve().parent))
