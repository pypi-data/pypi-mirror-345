import json
import warnings
import pycountry
from typing import Dict, Union
from helpers import DccConfiguration

def get_lang_flag(lang: str) -> str:
    """Returns the country flag emoji for a language code, or the code itself if no flag is available."""
    lang = lang.lower().strip()  # Normalize the input
    try:
        country_code = pycountry.languages.get(alpha_2=lang)
        if not country_code:
            return lang  # If language code is not found, return the code itself
        country_code = lang.upper()  # Convert language code to uppercase
        return chr(127397 + ord(country_code[0])) + chr(127397 + ord(country_code[1]))
    except (AttributeError, TypeError, IndexError):
        return lang  # Default to the language code if no emoji is available


class DccName(dict):
    """A dictionary subclass for handling multilingual names with enhanced functionality."""

    def __init__(self, content):
        parsedDict = {}
        try:
            content = content['dcc:name']
        except KeyError:
            pass
        if 'dcc:content' in content.keys():
            for item in content['dcc:content']:
                parsedDict[item['@lang']] = item['$']
        else:
            parsedDict = content
        return super().__init__(parsedDict)
    
    def __new__(cls, *args, **kwargs):
        if not args or args[0] is None:
            return None  # Ensure None is returned when initialized with None
        if len(args) == 1 and isinstance(args[0], DccName):
            return args[0]  # Return the exact same instance
        return super().__new__(cls)

    def __repr__(self):
        if DccConfiguration.reprStyle == "libDebug":
            return super().__repr__()

        for lang in DccConfiguration.preferredLangs:
            if lang in self:
                return f"{get_lang_flag(lang)} {self[lang]}"

        first_key = next(iter(self), None)
        return f"{first_key}: {self[first_key]}" if first_key else "<No Name>"

    def __str__(self):
        return json.dumps(self)

    def matches(self, other: Union['DccName', dict, str]) -> bool:
        if isinstance(other, (dict, DccName)):
            # Every key/value in 'other' must be present in self.
            for key, value in other.items():
                if key not in self or self[key] != value:
                    return False
            return True
        elif isinstance(other, str):
            # Check if any of the values in self match the string.
            return other in self.values()
        else:
            raise TypeError(f"Unsupported type {type(other)} for matching")

    def to_json_dict(self):
        return {'dcc:name':{'dcc:content': [{'@lang': key, '$': value} for key, value in dict(self).items()]}}

    def merge_names(self, insertion: str, other: Union['DccName', str, float, int, None]):
        """Merges two DccName instances or a DccName with another type, handling None gracefully."""
        merged = {}

        if other is None:
            other = {lang: "None" for lang in self}  # If other is None, use 'None' for all languages
        elif not isinstance(other, DccName):
            try:
                other = other.name  # Try using other.name if it exists
            except AttributeError:
                other = {lang: str(other) for lang in self}

        for lang in self:
            if lang in other:
                merged[lang] = f"{self[lang]} {insertion} {other[lang]}"

        if not merged:
            warnings.warn("No matching language found; using first available language as fallback.", RuntimeWarning)
            first_key = next(iter(other), None)
            if first_key:
                return {first_key: f"{first_key}: {other[first_key]}"}
            else:
                raise ValueError("Error in name generation; neither left nor right operand had valid names.")

        return merged

    def __add__(self, other):
        return DccName(self.merge_names("+", other))

    def __sub__(self, other):
        return DccName(self.merge_names("-", other))

    def __mul__(self, other):
        return DccName(self.merge_names("*", other))

    def __truediv__(self, other):
        return DccName(self.merge_names("/", other))

    def __radd__(self, other):
        return DccName(self.merge_names("+", other))

    def __rsub__(self, other):
        return DccName(self.merge_names("-", other))

    def __rmul__(self, other):
        return DccName(self.merge_names("*", other))

    def __rtruediv__(self, other):
        return DccName(self.merge_names("/", other))

    def __neg__(self):
        return DccName({lang: f"-{name}" for lang, name in self.items()})

    def __pos__(self):
        return DccName({lang: f"+{name}" for lang, name in self.items()})