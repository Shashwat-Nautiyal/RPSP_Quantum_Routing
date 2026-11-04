"""Minimal runner (use `pytest` if installed; this works without it)."""
import importlib, pkgutil, sys, time, traceback
sys.path.insert(0, ".")
import tests

failed = 0
for m in sorted(pkgutil.iter_modules(tests.__path__), key=lambda m: m.name):
    if not m.name.startswith("test_"):
        continue
    mod = importlib.import_module(f"tests.{m.name}")
    for name in sorted(dir(mod)):
        if name.startswith("test_"):
            t = time.time()
            try:
                getattr(mod, name)()
                print(f"PASS {m.name}::{name} ({time.time()-t:.1f}s)")
            except Exception:
                failed += 1
                print(f"FAIL {m.name}::{name}")
                traceback.print_exc()
print("FAILED" if failed else "ALL PASSED", failed)
sys.exit(1 if failed else 0)
