from dataclasses import dataclass, field
from math import ceil


@dataclass
class MessageSmartEncoding:
    """
    Sms Message Representation
    """

    replacements = {
        "“": '"',
        "”": '"',
        "‘": "'",
        "’": "'",
        "–": "-",
        "—": "-",
        "…": "...",
        "•": "-",
        "€": "EUR",
        "™": "",
        "©": "",
        "®": "",
        "\u0002": "",
        "\u001b": "",
    }
    body: str
    normalized_text: str = field(init=False)
    length: int = field(init=False)
    segments: int = field(init=False)

    def __post_init__(self):
        self.normalized_text = self.normalize(self.body)
        self.length = len(self.normalized_text)
        self.segments = ceil(self.length / 160)

    def normalize(self, text: str) -> str:
        for char, replacement in self.replacements.items():
            text = text.replace(char, replacement)
        return text
