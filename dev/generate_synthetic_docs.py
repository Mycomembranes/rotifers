import os
import sys
import pkgutil
import importlib
import inspect
import json

def _collect_docs(package):
    data = []
    prefix = package.__name__ + "."
    for modinfo in pkgutil.walk_packages(package.__path__, prefix):
        modname = modinfo.name
        try:
            module = importlib.import_module(modname)
        except Exception:
            # Skip modules that cannot be imported
            continue
        for name, obj in inspect.getmembers(module):
            if inspect.isfunction(obj) or inspect.isclass(obj):
                doc = inspect.getdoc(obj)
                if doc:
                    data.append({
                        "module": modname,
                        "name": name,
                        "docstring": doc
                    })
    return data

def main():
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    sys.path.insert(0, os.path.join(repo_root, "lib"))
    try:
        import rotifer.db.ncbi as ncbi
    except Exception as exc:
        raise SystemExit(f"Could not import rotifer package: {exc}")

    docs = _collect_docs(ncbi)
    out_dir = os.path.join(repo_root, "synthetic_data")
    os.makedirs(out_dir, exist_ok=True)
    out_file = os.path.join(out_dir, "ncbi_docs.json")
    with open(out_file, "w") as fh:
        json.dump(docs, fh, indent=2)
    print(f"Wrote {len(docs)} entries to {out_file}")

if __name__ == "__main__":
    main()
