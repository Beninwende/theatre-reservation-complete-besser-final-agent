"""
Generate programme_salle.md from data/shows.yaml (Lab 3-style generator).
"""
from pathlib import Path

from jinja2 import Environment, FileSystemLoader

_BASE = Path(__file__).resolve().parent


def main() -> None:
    import yaml

    with open(_BASE / "data" / "shows.yaml", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    env = Environment(loader=FileSystemLoader(str(_BASE / "templates")))
    tpl = env.get_template("programme.md.j2")
    out = tpl.render(shows=data.get("shows", []), title="Small theatre — programme")
    out_dir = _BASE / "out"
    out_dir.mkdir(exist_ok=True)
    (out_dir / "programme_salle.md").write_text(out, encoding="utf-8")
    print("Wrote", out_dir / "programme_salle.md")


if __name__ == "__main__":
    main()
