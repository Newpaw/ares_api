from urllib.parse import urlparse


def get_better_formated_domain(url: str) -> str:
    """
    This function takes a URL as input and returns just the domain.

    The input URL can be with or without a scheme (e.g., http:// or https://),
    with or without www, and may have additional paths after the domain.

    The function first checks if the URL contains a scheme. If not, it prepends 'http://'.

    Then the function uses Python's urlparse module to parse the URL and extract the network location (netloc).

    If the netloc starts with 'www.', this prefix is removed.

    The resulting domain is then returned.
    """

    if "://" not in url:
        url = "http://" + url
    parsed_uri = urlparse(url)
    domain = "{uri.netloc}".format(uri=parsed_uri)
    # Odstranění 'www.' pokud existuje
    if domain.startswith("www."):
        domain = domain[4:]
    return domain


def main():
    pass


if __name__ == "__main__":
    main()
