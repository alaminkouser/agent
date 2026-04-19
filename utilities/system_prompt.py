import datetime
from .skills import skills
from jinja2 import Environment, FileSystemLoader, select_autoescape
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
TEMPLATE_DIR = BASE_DIR / "system_prompt"

ENV = Environment(loader=FileSystemLoader(TEMPLATE_DIR), autoescape=select_autoescape())


def system_prompt():
    SKILLS_DISCOVER = skills.skills_discover()
    PROMPT = ENV.get_template("system_prompt.jinja2").render(
        current_time=datetime.datetime.now().strftime(
            "YEAR: %Y, MONTH: %m, DAY: %d, HOUR: %H, MINUTE: %M"
        ),
        skills_discover=SKILLS_DISCOVER,
    )
    print(PROMPT)
    return PROMPT
