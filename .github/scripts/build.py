"""
Build script for the DURF dashboards.

Exports each marimo notebook under notebooks/<slug>/notebook.py to
HTML/WebAssembly, using the export mode and metadata declared in that
notebook's metadata.json, then renders index.html.j2 into an index page
listing them all. Adapted from marimo's standard GitHub Pages template
(https://github.com/marimo-team/marimo-gh-pages-template) for a
per-notebook-folder-with-metadata.json layout instead of flat notebooks/
and apps/ directories.

Usage:
    uv run .github/scripts/build.py [--output-dir OUTPUT_DIR] [--template TEMPLATE]

The exported files are placed in --output-dir (default: _site).
"""

# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "jinja2==3.1.3",
#     "fire==0.7.0",
#     "loguru==0.7.0",
# ]
# ///

import json
import subprocess
from pathlib import Path
from typing import List, Union

import fire
import jinja2
from loguru import logger

# metadata.json "format" -> marimo export html-wasm flags
FORMATS = {
    "app": ["--mode", "run", "--no-show-code"],
    "notebook": ["--mode", "edit"],
}


def _export_html_wasm(notebook_path: Path, output_dir: Path, format: str) -> bool:
    """Export a single marimo notebook to HTML/WebAssembly format."""
    output_file = output_dir / Path(notebook_path.parent.name).with_suffix(".html")

    if format not in FORMATS:
        logger.error(f'format "{format}" not recognized, needs to be one of {list(FORMATS)}')
        return False

    cmd: List[str] = ["uvx", "marimo", "export", "html-wasm", "--sandbox", *FORMATS[format]]
    cmd.extend([str(notebook_path), "-o", str(output_file)])

    try:
        output_file.parent.mkdir(parents=True, exist_ok=True)
        logger.info(f"Exporting {notebook_path} to {output_file} as {format}")
        subprocess.run(cmd, capture_output=True, text=True, check=True)
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Error exporting {notebook_path}:\n{e.stderr}")
        return False


def _get_metadata(notebook_dir: Path) -> dict:
    with open(notebook_dir / "metadata.json") as f:
        metadata = json.load(f)
    metadata["html_path"] = str(Path(notebook_dir.name).with_suffix(".html"))
    metadata.setdefault("format", "app")
    return metadata


def _export(folder: Path, output_dir: Path) -> List[dict]:
    """Export every notebooks/<slug>/ directory to HTML/WebAssembly."""
    if not folder.exists():
        logger.warning(f"Directory not found: {folder}")
        return []

    notebook_dirs = sorted(p for p in folder.iterdir() if p.is_dir() and not p.name.startswith("_"))
    if not notebook_dirs:
        logger.warning(f"No notebooks found in {folder}!")
        return []

    notebook_data = []
    for notebook_dir in notebook_dirs:
        metadata = _get_metadata(notebook_dir)
        if _export_html_wasm(notebook_dir / "notebook.py", output_dir, metadata["format"]):
            notebook_data.append(metadata)

    logger.info(f"Successfully exported {len(notebook_data)} out of {len(notebook_dirs)} notebooks")
    return notebook_data


def _generate_index(output_dir: Path, template_file: Path, notebooks_data: List[dict]) -> None:
    logger.info("Generating index.html")
    env = jinja2.Environment(
        loader=jinja2.FileSystemLoader(template_file.parent),
        autoescape=jinja2.select_autoescape(["html", "xml"]),
    )
    template = env.get_template(template_file.name)
    rendered_html = template.render(notebooks=notebooks_data)
    (output_dir / "index.html").write_text(rendered_html)
    logger.info(f"Wrote {output_dir / 'index.html'}")


def main(
    output_dir: Union[str, Path] = "_site",
    template: Union[str, Path] = "index.html.j2",
) -> None:
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    notebooks_data = _export(Path("notebooks"), output_dir)
    if not notebooks_data:
        logger.warning("No notebooks found!")
        return

    _generate_index(output_dir=output_dir, template_file=Path(template), notebooks_data=notebooks_data)
    logger.info(f"Build completed successfully. Output directory: {output_dir}")


if __name__ == "__main__":
    fire.Fire(main)
