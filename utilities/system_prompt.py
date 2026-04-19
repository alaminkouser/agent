import datetime
from .skills import skills
from jinja2 import Environment, FileSystemLoader, select_autoescape

ENV = Environment(
    loader=FileSystemLoader("./utilities/system_prompt"),
    autoescape=select_autoescape()
) 


def system_prompt():
    SKILLS_DISCOVER = skills.skills_discover()
    PROMPT = ENV.get_template("system_prompt.jinja2").render(
        current_time=datetime.datetime.now().strftime(
            "YEAR: %Y, MONTH: %m, DAY: %d, HOUR: %H, MINUTE: %M"
        ),
        skills_discover=SKILLS_DISCOVER
    )
    return PROMPT
