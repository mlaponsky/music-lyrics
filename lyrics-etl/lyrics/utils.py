from typing import Dict, Optional, List, Iterable
import re
import os


def regex_factory(patterns: Dict[str, str],
                  ignore_case: bool = True) -> Dict[str, re.Pattern]:
    def regex_compiler(pattern: str) -> re.Pattern:
        if ignore_case:
            return re.compile(pattern, re.IGNORECASE)
        return re.compile(pattern)
    return {key: regex_compiler(pattern) for key, pattern in patterns.values()}


def strip_match(line: str, pattern: re.Pattern) -> Optional[str]:
    match: re.Match = pattern.match(line)
    if not match:
        return None
    result: str = line[:match.start()] + line[match.end():]
    return result.strip()


def get_files(root_dir: str) -> Iterable[str]:
    return (os.path.join(root, filename) for root, _, filenames in os.walk(root_dir)
            for filename in filenames)
