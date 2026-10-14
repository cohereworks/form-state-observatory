from pathlib import Path
from fontTools.ttLib import TTFont

BASE = Path(__file__).resolve().parents[1] / 'experiments/font-state/v2/generated'


def test_generated_font_tables():
    required = ['ProbeMetric', 'ProbeToken', 'ProbeContext', 'ProbeTokenContext', 'ProbeAddress']
    for name in required:
        assert (BASE / f'{name}.woff2').is_file(), f'Missing generated asset: {name}'
        font = TTFont(BASE / f'{name}.ttf')
        assert font['head'].unitsPerEm == 1000
        assert font['hmtx'].metrics
        if name == 'ProbeAddress':
            assert [a.axisTag for a in font['fvar'].axes] == ['ADDR']
            assert hasattr(font['GSUB'].table, 'FeatureVariations')
        font.close()
