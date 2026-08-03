"""Live Dragon probe: verify choice-0 rule numbers (dwWordNum vs dwCFGParse)
plus a handful of exception-class parity checks.

Not collected by pytest (no test_ prefix) — it needs a live Dragon and mimics
speech, so it is run by hand:

    .venv/Scripts/python.exe tests/manual_probe_cfgparse.py

Output goes to the real stderr because natConnect redirects sys.stdout.
"""
import os
import sys
import time

if not hasattr(sys, 'coinit_flags'):
    sys.coinit_flags = 2

import comtypes.client
comtypes.client.gen_dir = None

sys.path.insert(0, os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))

import natlink_compat as natlink
from natlink_compat._state import _state
from natlink_com._res_obj import _best_path_word, _get_word_node
from natlink_com.grammar_compiler import compile_grammar


class _NullUI:
    def on_state_changed(self, state): pass
    def on_text(self, text, level=20): pass


def _p(*a):
    """Print to the real stderr — natConnect replaces sys.stdout/sys.stderr."""
    print(*a, file=sys.__stderr__, flush=True)


def main():
    if _state.ui_provider is None:
        _state.ui_provider = _NullUI()
    natlink.natConnect(discovered_loaders=[])
    _p("connected; mic state:", natlink.getMicState())

    results = {}

    # Two exported rules so rule numbers are distinguishable (1 and 2),
    # plus shared word 'now' appearing in both rules.
    spec = ("<ruleOne> exported = hello world now;\n"
            "<ruleTwo> exported = goodbye now;\n")
    binary = compile_grammar(spec)

    gram = natlink.GramObj()
    received = []
    gram.setResultsCallback(lambda words, res: received.append((words, res)))
    gram.load(binary)
    gram.activate("ruleOne", 0)
    gram.activate("ruleTwo", 0)
    try:
        gram.setExclusive(1)
    except Exception as e:
        _p("setExclusive failed (continuing):", e)

    try:
        # ---- Experiment 1: mimic ruleTwo, compare cached vs graph ----
        natlink.recognitionMimic(["goodbye", "now"])
        deadline = time.monotonic() + 5
        from natlink_com._pump import pump
        while time.monotonic() < deadline and not received:
            pump()
            time.sleep(0.01)
        if not received:
            _p("FAIL: results callback never fired")
            return 1

        words, res = received[-1]
        proxy = res._proxy
        _p("\n--- callback words (what natlinkutils/dragonfly see):", words)

        cached = proxy.get_results(0)
        _p("cached choice-0 (SRPHRASEW dwWordNum):", cached)

        graph = proxy._qi("ISRResGraphW")
        if graph is None:
            _p("FAIL: no ISRResGraphW on result object")
        else:
            path, count = _best_path_word(graph, 0)
            graph_words = []
            for i in range(count):
                node, text = _get_word_node(graph, path[i], proxy._tlb)
                if node is not None:
                    graph_words.append({
                        "word": text,
                        "dwCFGParse": node.dwCFGParse,
                        "dwWordNum": getattr(node, "dwWordNum", None),
                    })
            _p("graph choice-0 (BestPathWord/GetWordNode):", graph_words)
            results["exp1"] = (cached, graph_words)

        # mimic ruleOne too, second data point (3 words, different rule)
        received.clear()
        natlink.recognitionMimic(["hello", "world", "now"])
        deadline = time.monotonic() + 5
        while time.monotonic() < deadline and not received:
            pump()
            time.sleep(0.01)
        if received:
            words2, res2 = received[-1]
            proxy2 = res2._proxy
            cached2 = proxy2.get_results(0)
            graph2 = proxy2._qi("ISRResGraphW")
            path2, count2 = _best_path_word(graph2, 0)
            gw2 = []
            for i in range(count2):
                node, text = _get_word_node(graph2, path2[i], proxy2._tlb)
                if node is not None:
                    gw2.append({"word": text, "dwCFGParse": node.dwCFGParse})
            _p("\nruleOne cached:", cached2)
            _p("ruleOne graph :", gw2)

            # ---- Experiment 2: OutOfRange behavior on exhausted choice ----
            _p("\n--- getResults(50) behavior ---")
            try:
                r = res2.getResults(50)
                _p("compat getResults(50) returned:", r)
            except Exception as e:
                _p("compat getResults(50) raised:", type(e).__name__, e)
            try:
                r = proxy2.get_results(50)
                _p("com get_results(50) returned:", r)
            except Exception as e:
                _p("com get_results(50) raised:", type(e).__name__,
                      "error_type=", getattr(e, 'error_type', None), e)

        # ---- Experiment 3: execScript syntax error class ----
        _p("\n--- execScript bad syntax ---")
        try:
            natlink.execScript("This is not a valid script (((")
        except Exception as e:
            _p("execScript raised:", type(e).__name__, e)

        # ---- Experiment 4: activate on bogus hwnd ---
        _p("\n--- activate with stale hwnd ---")
        g2 = natlink.GramObj()
        g2.load(compile_grammar("<r> exported = test phrase;"))
        try:
            g2.activate("r", 0x00DEAD00)
        except Exception as e:
            _p("activate(bad hwnd) raised:", type(e).__name__, e)
        finally:
            g2.unload()

    finally:
        try:
            gram.setExclusive(0)
        except Exception:
            pass
        gram.unload()
        natlink.natDisconnect()
        _p("\ndisconnected cleanly")
    return 0


if __name__ == "__main__":
    sys.exit(main())
