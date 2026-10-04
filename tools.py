import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse


def classify_source(
    url: str
) -> str:

    if not url:

        return "Unknown"

    try:

        domain = urlparse(
            url
        ).netloc.lower()

    except Exception:

        return "Unknown"

    official_domains = [
        ".gov",
        ".gov.pk",
        ".edu",
        ".edu.pk",
        ".ac.uk",
        ".gov.uk",
    ]

    if any(
        domain.endswith(
            suffix
        )
        for suffix in official_domains
    ):

        return "Official"

    return "Secondary"


def read_webpage(
    url: str,
    max_chars: int = 10000,
) -> str:

    try:

        response = requests.get(
            url,
            timeout=15,
            headers={
                "User-Agent":
                    "NexStepAI/1.0"
            },
        )

        response.raise_for_status()

        soup = BeautifulSoup(
            response.text,
            "html.parser"
        )

        for element in soup(
            [
                "script",
                "style",
                "noscript",
                "nav",
                "footer",
            ]
        ):

            element.decompose()

        text = soup.get_text(
            separator=" ",
            strip=True,
        )

        return text[:max_chars]

    except Exception as e:

        return (
            f"Unable to read webpage: {e}"
        )


def document_status(
    required_documents,
    uploaded_documents,
):

    uploaded_lower = [
        name.lower()
        for name in uploaded_documents
    ]

    results = []

    for document in required_documents:

        name = document.lower()

        found = any(
            name in uploaded
            or uploaded in name
            for uploaded in uploaded_lower
        )

        if found:

            results.append(
                {
                    "name": document,
                    "status": "Available",
                }
            )

        else:

            results.append(
                {
                    "name": document,
                    "status": "Missing",
                }
            )

    return results
