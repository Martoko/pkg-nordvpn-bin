from collections.abc import Sequence
import re


class Maintainer:
    def __init__(self, name, email):
        self.name = name
        self.email = email

    def __str__(self):
        return f"# Maintainer: {self.name} <{self.email}>"


class Attribute:
    def __init__(self, key, value):
        self.key = key
        self.value = value

    def __str__(self):
        if isinstance(self.value, str):
            return f"{self.key}={self.value}"
        if isinstance(self.value, Sequence):
            return f"""{self.key}=({' '.join(self.value)})"""


class Function:
    def __init__(self, name, lines):
        self.name = name
        self.body = "\n".join([' ' * 4 + l for l in lines])

    def __str__(self):
        return f"{self.name}() {{\n{self.body}\n}}"


class Version:
    def __init__(self, string):
        regex = r"([0-9]+)\.([0-9]+)\.([0-9]+)[-_]([0-9]+)"
        match = re.search(regex, string)
        self.major = match[1]
        self.minor = match[2]
        self.patch = match[3]
        self.upstream_revision = match[4]

    def aur_str(self):
        return f"{self.major}.{self.minor}.{self.patch}_{self.upstream_revision}"

    def upstream_str(self):
        return f"{self.major}.{self.minor}.{self.patch}-{self.upstream_revision}"

    def __eq__(self, other):
        if not isinstance(other, Version):
            return False

        return self.major == other.major and \
               self.minor == other.minor and \
               self.patch == other.patch and \
               self.upstream_revision == other.upstream_revision


class Pkgbuild:
    def __init__(self):
        self.maintainers = []
        self.attributes = []
        self.functions = []

    def __str__(self):
        maintainers = "\n".join([str(m) for m in self.maintainers])
        attributes = "\n".join([str(m) for m in self.attributes])
        functions = "\n\n".join([str(m) for m in self.functions])

        return "\n\n".join([maintainers, attributes, functions])
