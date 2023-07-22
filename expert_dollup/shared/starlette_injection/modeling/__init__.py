import re
from pydantic import BaseModel


UNDERSCORE_RE = re.compile(r"(?<=[^\-_])[\-_]+[^\-_]")


def _is_none(_in):
    """
    Determine if the input is None
    and returns a string with white-space removed
    :param _in: input
    :return:
        an empty sting if _in is None,
        else the input is returned with white-space removed
    """
    return "" if _in is None else re.sub(r"\s+", "", str(_in))


def to_camel(string):
    """
    Convert a string, dict, or list of dicts to camel case.
    :param str_or_iter:
        A string or iterable.
    :type str_or_iter: Union[list, dict, str]
    :rtype: Union[list, dict, str]
    :returns:
        camelized string, dictionary, or list of dictionaries.
    """
    s = _is_none(string)
    if s.isupper() or s.isnumeric():
        return string

    if len(s) != 0 and not s[:2].isupper():
        s = s[0].lower() + s[1:]

    # For string "hello_world", match will contain
    #             the regex capture group for "_w".
    return UNDERSCORE_RE.sub(lambda m: m.group(0)[-1].upper(), s)


class CamelModel(BaseModel):
    class Config:
        alias_generator = to_camel
        allow_population_by_field_name = True


class GeneriCamelModel(BaseModel):
    class Config:
        alias_generator = to_camel
        allow_population_by_field_name = True
