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
        regex = r"([0-9]+)\.([0-9]+)\.([0-9]+)([-_]([0-9]+))?"
        match = re.search(regex, string)
        self.major = int(match[1])
        self.minor = int(match[2])
        self.patch = int(match[3])
        self.upstream_revision = int(match[5]) if match[5] is not None else None

    def aur_str(self):
        if self.upstream_revision is None:
            return f"{self.major}.{self.minor}.{self.patch}"
        else:
            return f"{self.major}.{self.minor}.{self.patch}_{self.upstream_revision}"

    def upstream_str(self):
        if self.upstream_revision is None:
            return f"{self.major}.{self.minor}.{self.patch}"
        else:
            return f"{self.major}.{self.minor}.{self.patch}-{self.upstream_revision}"

    def __repr__(self):
        return self.upstream_str()

    def __eq__(self, other):
        if not isinstance(other, Version):
            return False

        return self.major == other.major and \
               self.minor == other.minor and \
               self.patch == other.patch and \
               self.upstream_revision == other.upstream_revision

    def __ne__(self, other):
        return not self == other

    def __lt__(self, other):
        if not isinstance(other, Version):
            return False

        if self.major < other.major:
            return True

        if self.major == other.major and \
           self.minor < other.minor:
            return True

        if self.major == other.major and \
           self.minor == other.minor and \
           self.patch < other.patch:
            return True

        if self.major == other.major and \
           self.minor == other.minor and \
           self.patch == other.patch:
            if self.upstream_revision is None and other.upstream_revision is not None:
                return True
            if self.upstream_revision is not None and other.upstream_revision is not None:
                if self.upstream_revision < other.upstream_revision:
                    return True

        return False

    def __gt__(self, other):
        return self != other and not self < other

    def __le__(self, other):
        return self == other or self < other

    def __ge__(self, other):
        return self == other or self > other


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


if __name__ == '__main__':
    for v in ['3.7.1', '3.3.1-1', '3.7.0-3', '3.7.0-0']:
        print(v)
        print('AUR: ' + Version(v).aur_str())
        print('Upstream: ' + Version(v).upstream_str())
