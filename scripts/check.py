"""Validate the extension and its three theme variants against Zed's schema."""

import json
from pathlib import Path
import re
import sys
import tomllib

import jsonschema


root = Path(__file__).resolve().parents[1]
manifest_path = root / "extension.toml"
assert manifest_path.is_file(), "Missing extension.toml"
manifest = tomllib.loads(manifest_path.read_text())
assert manifest["id"] == "ethereal-theme"
assert manifest["schema_version"] == 1
assert re.fullmatch(r"\d+\.\d+\.\d+", manifest["version"])
assert manifest["repository"] == "https://github.com/khdobromir/zed-ethereal"
assert manifest["authors"] and manifest["description"]
assert manifest["themes"] == ["themes/ethereal.json"]
assert (root / "LICENSE").is_file()

schema = json.loads(Path(sys.argv[1]).read_text())
family = json.loads((root / manifest["themes"][0]).read_text())
jsonschema.validate(family, schema)
assert family["$schema"] == "https://zed.dev/schema/themes/v0.2.0.json"
themes = {theme["name"]: theme["style"] for theme in family["themes"]}
assert len(family["themes"]) == len(themes) == 3, "Duplicate or missing variants"
assert set(themes) == {"Ethereal Blur", "Ethereal Regular", "Ethereal Material"}
surfaces = (
    "background", "editor.background", "editor.gutter.background",
    "panel.background", "terminal.background", "tab_bar.background",
)
for name, style in themes.items():
    assert style["syntax"] == themes["Ethereal Blur"]["syntax"]
    assert style["text"] == "#ffcead"
    assert style["text.accent"] == "#7d82d9"
    for value in re.findall(r'"(#[^"\s]*)"', json.dumps(style)):
        assert re.fullmatch(r"#[\da-fA-F]{6}([\da-fA-F]{2})?", value), value
    if name == "Ethereal Blur":
        assert style["background.appearance"] == "blurred"
        assert style["background"] == "#060b1edd"
        for key in surfaces[1:]:
            assert style[key] == "#060b1e00", key
    else:
        assert style["background.appearance"] == "opaque"
        for key in surfaces:
            assert len(style[key]) == 7 or style[key][7:].lower() == "ff", key

regular, material = themes["Ethereal Regular"], themes["Ethereal Material"]
assert regular["panel.background"] != regular["editor.background"]
assert regular["title_bar.background"] != regular["editor.background"]
assert material["panel.background"] == material["editor.background"]
assert material["title_bar.background"] == material["editor.background"]
print("PASS: manifest, Zed schema, three variants, palette and surface opacity")
