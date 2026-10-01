import sys

from linkcheck.checker import LinkCheckError, check_url


def main(argv=None):
    urls = sys.argv[1:] if argv is None else argv
    broken = []
    for url in urls:
        try:
            ok = check_url(url)
        except LinkCheckError:
            ok = False
        if not ok:
            broken.append(url)
            print(f"BROKEN {url}")
    if broken:
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
