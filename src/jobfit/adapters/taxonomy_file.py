import json
from importlib.resources import files

from jobfit.domain.taxonomy import Taxonomy, build_taxonomy


def load_default_taxonomy() -> Taxonomy:
    raw = files("jobfit").joinpath("data/taxonomy.json").read_text(encoding="utf-8")
    payload = json.loads(raw)
    return build_taxonomy(payload["version"], payload["skills"])
