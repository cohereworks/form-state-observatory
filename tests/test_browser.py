"""Read-only automated observation of declarative browser behavior.

The test runner is intentionally imperative; the *demonstration* page contains
no JavaScript. These observations do not silently become success claims.
"""
import json
import os
import platform
import hashlib
from pathlib import Path

import pytest
from playwright.sync_api import sync_playwright

BASE_URL = os.environ.get('PROBE_BASE_URL', 'http://127.0.0.1:8765')
ROOT = Path(__file__).resolve().parents[1]


def snapshot(page, selector, meter=None):
    """Instrument widths and generated content, never modify app state."""
    return page.evaluate("""({selector, meter}) => {
      const el = document.querySelector(selector);
      if (!el) return {missing:selector};
      const style = getComputedStyle(el);
      const m = meter && document.querySelector(meter);
      const out = m?.querySelector('.readout');
      const rect = el.getBoundingClientRect();
      return {
        inputWidth:rect.width,
        inputHeight:rect.height,
        fontSize:style.fontSize,
        fontFamily:style.fontFamily,
        variations:style.fontVariationSettings,
        meterWidth:m?.getBoundingClientRect().width ?? null,
        decode:out ? getComputedStyle(out,'::before').content : null,
        fontLoaded:document.fonts.check(`${style.fontSize} ${style.fontFamily.split(',')[0]}`)
      };
    }""", {'selector': selector, 'meter': meter})


def classify(observed, expected, canary=True):
    if not canary:
        return 'inconclusive: prerequisite unsupported'
    return 'observed' if observed else 'falsified'


def test_browser_observations(browser_name):
    out = ROOT / 'artifacts' / browser_name
    out.mkdir(parents=True, exist_ok=True)
    report = {'browser':browser_name, 'cases':{}, 'consoleErrors':[], 'runtime':{}, 'sourceCommit':os.getenv('GITHUB_SHA'), 'operatingSystem':platform.platform()}
    with sync_playwright() as playwright:
        browser = getattr(playwright, browser_name).launch(headless=True)
        page = browser.new_page(viewport={'width':1365,'height':950}, device_scale_factor=1)
        page.on('pageerror', lambda e: report['consoleErrors'].append(str(e)))
        report['browserVersion'] = browser.version
        report['assets'] = {p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in (ROOT/'experiments/font-state/v2/generated').glob('*.woff2')}
        trace = out / 'trace.zip'
        page.context.tracing.start(screenshots=True, snapshots=True, sources=True)
        try:
            response = page.goto(BASE_URL+'/experiments/font-state/v2/index.html', wait_until='load', timeout=30000)
            assert response and response.status == 200
            assert page.locator('#metric').count() == 1
            assert page.locator('script').count() == 0, 'Experiment must remain zero JS'
            page.evaluate('document.fonts.ready')
            report['runtime'] = page.evaluate("""() => ({
                userAgent:navigator.userAgent,
                platform:navigator.platform,
                supports: {
                    fieldSizing:CSS.supports('field-sizing:content'),
                    anchorSize:CSS.supports('width:anchor-size(--p width,1px)'),
                    timeline:CSS.supports('animation-timeline:scroll()'),
                    timelineScope:CSS.supports('timeline-scope:--probe'),
                    variation:CSS.supports('font-variation-settings:"ADDR" 2')
                }
            })""")
            support = report['runtime']['supports']
            # A native text control must respond to actual user input.
            metric = page.locator('#metric')
            metric.fill('A')
            page.wait_for_timeout(200)
            m1 = snapshot(page,'#metric','.metric-meter')
            metric.fill('ABCDEFGH')
            page.wait_for_timeout(200)
            m8 = snapshot(page,'#metric','.metric-meter')
            assert metric.input_value() == 'ABCDEFGH', 'Native input editing failed'
            report['cases']['metricWidthChange'] = {'classification':classify(m8['inputWidth'] > m1['inputWidth'],support['fieldSizing']), 'deltaPx':m8['inputWidth']-m1['inputWidth']}
            report['cases']['metric'] = {'one':m1,'eight':m8,
                'classification':classify('1 glyph' in (m1['decode'] or '') and '8 glyphs' in (m8['decode'] or ''),support['fieldSizing'] and support['anchorSize'])}
            # Actual substitutions may depend on live-editor shaping policy.
            for token in ('ALICE','BOB','CAROL','DAVE'):
                page.locator('#token').fill(token)
                page.locator('#token-calt').fill(token)
                page.wait_for_timeout(100)
                report['cases'].setdefault('tokenLiga',{})[token] = snapshot(page,'#token','.token-meter')
                report['cases'].setdefault('tokenCalt',{})[token] = snapshot(page,'#token-calt','.token-calt-meter')
            # Compare noncommutative results; record decoder value as separate evidence.
            for text in ('^','^A','^AB','^BA','^ABC','^CBA'):
                page.locator('#context').fill(text)
                page.wait_for_timeout(100)
                report['cases'].setdefault('context',{})[text] = snapshot(page,'#context','.context-meter')
            context = report['cases']['context']
            report['cases']['contextOrder'] = {
                'classification':classify(context['^AB']['inputWidth'] != context['^BA']['inputWidth'], support['fieldSizing']),
                'AB':context['^AB']['inputWidth'],'BA':context['^BA']['inputWidth']}
            # Isolate variable axis effects: same literal input throughout.
            for addr in (1,2,3):
                page.locator(f'#addr-{addr}').check()
                page.wait_for_timeout(150)
                report['cases'].setdefault('manualAddress',{})[str(addr)] = snapshot(page,'#address-manual','.address-manual-meter')
            vals = [report['cases']['manualAddress'][str(n)]['inputWidth'] for n in (1,2,3)]
            report['cases']['manualAddressResult'] = {
                'classification':classify(vals[0]<vals[1]<vals[2],support['variation'] and support['fieldSizing']),
                'widths':vals}
            # Explicit programmatic scrolling is *test actuation* of native scroll state,
            # not application implementation; CSS still owns the font-state projection.
            box = page.locator('.v2-scrollbox')
            for frac in (0,0.5,1):
                box.evaluate('(el,f) => { el.scrollLeft=(el.scrollWidth-el.clientWidth)*f }',frac)
                page.wait_for_timeout(350)
                report['cases'].setdefault('scrollAddress',{})[str(frac)] = {
                    'scrollLeft':box.evaluate('(el)=>el.scrollLeft'),
                    'progressWidth':page.locator('.v2-progress > div').evaluate('(el)=>el.getBoundingClientRect().width'),
                    'token':snapshot(page,'#scroll-token-v2','.v2-scroll-meter'),
                    'address':snapshot(page,'#address-scroll-v2','.v2-address-meter')}
            scroll = report['cases']['scrollAddress']
            p0,p1=scroll['0']['progressWidth'],scroll['1']['progressWidth']
            report['cases']['scrollProgressResult'] = {
                'classification': classify(p1 > p0+5, support['timeline'] and support['timelineScope']),
                'progressStart':p0,'progressEnd':p1}
            report['cases']['scrollAddressResult'] = {
                'classification': classify(scroll['0']['address']['inputWidth'] != scroll['1']['address']['inputWidth'], support['timeline'] and support['variation']),
                'startWidth':scroll['0']['address']['inputWidth'],'endWidth':scroll['1']['address']['inputWidth']}
            page.screenshot(path=str(out/'font-state-v2.png'), full_page=True)
            page.goto(BASE_URL+'/experiments/font-state/v1/index.html',wait_until='load')
            page.screenshot(path=str(out/'font-state-v1.png'),full_page=True)
            page.goto(BASE_URL+'/experiments/geometric-oracles/range-and-textarea.html',wait_until='load')
            page.screenshot(path=str(out/'geometric-oracles.png'),full_page=True)
            page.goto(BASE_URL+'/experiments/geometric-oracles/live-text.html',wait_until='load')
            page.screenshot(path=str(out/'live-text.png'),full_page=True)
        finally:
            (out/'evidence.json').write_text(json.dumps(report,indent=2,sort_keys=True),encoding='utf8')
            page.context.tracing.stop(path=str(trace))
            browser.close()
    # Never require research claims to hold merely to get a green CI run.
    assert report['runtime']['userAgent'], 'Missing browser evidence'
