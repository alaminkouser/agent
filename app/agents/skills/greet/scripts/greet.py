#!/usr/bin/env python

import argparse
from dataclasses import dataclass


@dataclass
class GreetInput:
    name_first: str
    name_last: str


def greet(input: GreetInput) -> str:
    return f"Hello {input.name_first}. Your full name is: {input.name_first} {input.name_last}."


def main() -> str:
    parser = argparse.ArgumentParser(description="Greet People")
    parser.add_argument(
        "--name-first",
        type=str,
        required=True,
        help="First Name",
    )
    parser.add_argument(
        "--name-last",
        type=str,
        required=True,
        help="Last Name",
    )

    args = parser.parse_args()
    print(greet(input=GreetInput(name_first=args.name_first, name_last=args.name_last)))


if __name__ == "__main__":
    main()
