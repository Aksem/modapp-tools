import re

pattern = re.compile(r'(?<!^)(?=[A-Z])')


def to_snake_case(string: str):
    return pattern.sub('_', string).lower()
