from jinja2 import Environment, FileSystemLoader
from pathlib import Path

template_env = Environment(
    loader=FileSystemLoader(
        Path(Path(__file__).resolve().parent).joinpath("..", "templates").resolve()
    )
)
