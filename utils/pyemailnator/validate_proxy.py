from better_proxy import Proxy


def validate_proxy(proxy: str | None) -> str | None:
    if not proxy:
        return None

    try:
        return Proxy.from_str(proxy=proxy).as_url

    except ValueError:
        return None