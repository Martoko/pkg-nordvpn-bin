#!/usr/bin/env bash
set -eu # Exit on errors and throw errors when acessing unset variables

usage() {
	echo "usage: $(basename $0) [options]"
	echo "options:"
	echo "  -n, --no-act         disable running git push"
	exit 1
}

DRY=
# Parse arguments
while test $# != 0; do
	case "$1" in
	-n|--no-act) DRY=t ;;
	*) usage ;;
	esac
	shift
done

echo "Updating package repo from AUR..." >&2
if [ -d nordvpn-bin ]; then
	cd nordvpn-bin
	{ git fetch origin && git reset --hard origin/master; } || exit 1
else
	git clone --depth 1 ssh://aur@aur.archlinux.org/nordvpn-bin.git
	cd nordvpn-bin
fi

echo "Reading existing current version from PKGBUILD..." >&2
source PKGBUILD

echo "Getting latest version from upstream..." >&2
# Gets the list of packages, greps the 'Version: ' field, cuts off the prefix,
# sorts by 'version order', takes the latest version.
new_pkgver=$(curl 'https://repo.nordvpn.com/deb/nordvpn/debian/dists/stable/main/binary-amd64/Packages' |
             grep '^Version: ' | cut -d' ' -f2 | sort -V | tail -n 1)
# `-`'s are not allowed in pkgvers, so we substitute with `_`
new_pkgver="${new_pkgver//-/_}"

# If we are already up to date, simply print version and exit
if [ "$pkgver" = "$new_pkgver" ]; then
	echo "Package is up to date with upstream ($pkgver)" >&2
	exit
fi

echo "Updating PKGBUILD..." >&2
sed -i -E "s/^pkgver=.*\$/pkgver=${new_pkgver}/" PKGBUILD
sed -i -E "s/^pkgrel=.*\$/pkgrel=1/" PKGBUILD
echo "Updating package checksums..." >&2
updpkgsums
echo "Building package..." >&2
makepkg -f
echo "Updating .SRCINFO..." >&2
makepkg --printsrcinfo > .SRCINFO
echo "Checking with namcap..." >&2
# namcap PKGBUILD
namcap "nordvpn-bin-${new_pkgver}-1-x86_64.pkg.tar.zst"
echo "Commiting changes..." >&2
git add .SRCINFO PKGBUILD
git commit -m "Update to $new_pkgver"
echo "Updating from $pkgver to $new_pkgver..." >&2
[ -z "$DRY" ] && git push >&2
