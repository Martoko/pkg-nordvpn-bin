#!/usr/bin/env python
from urllib.request import Request, urlopen
import os
import sys
from pkgbuild import *

dry = len(sys.argv) > 1 and sys.argv[1] == "--dry"


def run_or_die(command):
    code = os.system(command)
    if code != 0:
        print(f"error return code was not 0, command: {command}")
        exit(1)


def get_current_version():
    with open("PKGBUILD", "r") as f:
        for line in f:
            if line.startswith("pkgver"):
                return Version(line.split("=")[1])


def get_latest_version():
    REPO_URL = 'https://repo.nordvpn.com/deb/nordvpn/debian/dists/stable/main/binary-amd64/Packages'

    # The default user-agent is blocked, so we pretend to be a Firefox browser
    def fetch(url):
        return urlopen(Request(url, headers={'User-Agent': 'Mozilla/5.0'})).read().decode('utf-8')

    # Read the repo
    repo = fetch(REPO_URL)

    # Make array of packages
    packages = repo.split('\n\n')

    # Split package into "key: value" lines
    packages = [package.split('\n') for package in packages]

    # Convert "key: value" lines to dict
    def package_to_dict(package):
        package_dict = {}
        for entry in package:
            key, _, value = entry.partition(':')
            package_dict[key] = value.strip()
        return package_dict

    packages = [package_to_dict(package) for package in packages]

    # Find the most recent version
    packages.sort(key=lambda p: Version(p["Version"]), reverse=True)

    return Version(packages[0]["Version"])


if os.path.exists("nordvpn-bin"):
    os.chdir("nordvpn-bin")
    run_or_die("git fetch origin && git reset --hard origin/master")
else:
    run_or_die("git clone --depth 1 ssh://aur@aur.archlinux.org/nordvpn-bin.git")
    os.chdir("nordvpn-bin")

latest_version = get_latest_version()
current_version = get_current_version()

if latest_version == current_version and not dry:
    print("Current version is the latest version, no update necessary")
    exit(0)

pkgbuild = Pkgbuild()
pkgbuild.maintainers += [
    Maintainer("metiis", "aur at metiis dot com"),
    Maintainer("Julio Gutierrez", "bubuntux at gmail dot com"),
    Maintainer("Martoko", "mbastholm at gmail dot com")
]
pkgbuild.attributes += [
    Attribute("pkgname", "nordvpn-bin"),
    Attribute("pkgver", latest_version.aur_str()),
    Attribute("pkgrel", "1"),
    Attribute("pkgdesc", "\"NordVPN CLI tool for Linux\""),
    Attribute("arch", ["'x86_64'", "'i686'", "'armv7h'", "'aarch64'"]),
    Attribute("url", "\"https://nordvpn.com/download/linux/\""),
    Attribute("license", ["'custom'"]),
    Attribute("depends", ["'libxslt'", "'iptables'", "'procps'", "'iproute2'",
                          "'ipset'", "'ca-certificates'"]),
    Attribute("provides", ["'nordvpn'"]),
    Attribute("conflicts", ["'openvpn-nordvpn'"]),
    Attribute("install", "nordvpn-bin.install"),
    # Mapping between debian arch names and archlinux arch names
    # source: amd64 - x86_64
    # source: i386 - i686
    # source: armel - arm
    # source: armel - armv6h
    # source: armhf - armv7h
    # source: arm64 - aarch64
    Attribute("source_x86_64",
              ["\"https://repo.nordvpn.com/deb/nordvpn/debian/pool/main/nordvpn_${pkgver//_/-}_amd64.deb\""]),
    Attribute("source_i686",
              ["\"https://repo.nordvpn.com/deb/nordvpn/debian/pool/main/nordvpn_${pkgver//_/-}_i386.deb\""]),
    # Attribute("source_arm",
    #           ["\"https://repo.nordvpn.com/deb/nordvpn/debian/pool/main/nordvpn_${pkgver//_/-}_armel.deb\""]),
    # Attribute("source_armv6h",
    #           ["\"https://repo.nordvpn.com/deb/nordvpn/debian/pool/main/nordvpn_${pkgver//_/-}_armel.deb\""]),
    Attribute("source_armv7h",
              ["\"https://repo.nordvpn.com/deb/nordvpn/debian/pool/main/nordvpn_${pkgver//_/-}_armhf.deb\""]),
    Attribute("source_aarch64",
              ["\"https://repo.nordvpn.com/deb/nordvpn/debian/pool/main/nordvpn_${pkgver//_/-}_arm64.deb\""]),
    Attribute("sha256sums_x86_64", ['update me']),
    Attribute("sha256sums_i686", ['update me']),
    # Attribute("sha256sums_arm", ['update me']),
    # Attribute("sha256sums_armv6h", ['update me']),
    Attribute("sha256sums_armv7h", ['update me']),
    Attribute("sha256sums_aarch64", ['update me'])
]

pkgbuild.functions += [Function("package", [
    'bsdtar -O -xf *.deb data.tar.gz | bsdtar -C "${pkgdir}" -xJf -',
    '',
    'mv "${pkgdir}/usr/sbin/nordvpnd" "${pkgdir}/usr/bin"',
    'rm -r "${pkgdir}/etc/init.d"',
    'rm -r "${pkgdir}/usr/sbin"',
    'echo "g nordvpn - -" | install -Dm644 /dev/stdin "${pkgdir}/usr/lib/sysusers.d/${pkgname}.conf"'
])]

with open("PKGBUILD", "w") as f:
    f.write(str(pkgbuild))

run_or_die("updpkgsums")

run_or_die("makepkg -f")
# TODO: Write a test that checks everything still works in the new version

run_or_die("makepkg --printsrcinfo > .SRCINFO")
run_or_die("git add .SRCINFO PKGBUILD")
run_or_die(f"git commit -m 'Update to {latest_version.upstream_str()}'")

print(f"Updating from {current_version.upstream_str()} to {latest_version.upstream_str()}")

# if latest_version.major != current_version.major or latest_version.minor != current_version.minor:
#     print("Refusing to automatically update a major or minor version")
#     exit(1)
if latest_version.major != current_version.major:
    print("Refusing to automatically update a major version")
    exit(1)
else:
    if not dry:
        run_or_die("git push")
