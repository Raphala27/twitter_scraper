from __future__ import annotations
import re
from typing import List, Dict, Any, Callable


class DetectionRule:
    def __init__(self, name: str, pattern: str, action: Callable[[Dict[str, Any]], Dict[str, Any]]):
        self.name = name
        self.regex = re.compile(pattern, re.IGNORECASE)
        self.action = action

    def match(self, text: str) -> bool:
        return bool(self.regex.search(text))


class RulesDetector:
    """Extensible detector; register DetectionRule instances."""

    def __init__(self) -> None:
        self.rules: List[DetectionRule] = []

    def register(self, rule: DetectionRule) -> None:
        self.rules.append(rule)

    def detect(self, post: Dict[str, Any]) -> List[Dict[str, Any]]:
        text = post.get("full_text", "")
        findings: List[Dict[str, Any]] = []
        for rule in self.rules:
            if rule.match(text):
                result = rule.action(post)
                findings.append({"rule": rule.name, "result": result})
        return findings
