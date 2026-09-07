import io
import zipfile

import httpx

from app.config import settings


def fetch_run_logs(owner: str, repo: str, github_run_id: int, tail_lines: int = 50) -> str:
    url = f"https://api.github.com/repos/{owner}/{repo}/actions/runs/{github_run_id}/logs"
    headers = {
        "Authorization": f"Bearer {settings.github_token}",
        "Accept": "application/vnd.github+json",
    }

    response = httpx.get(url, headers=headers, follow_redirects=True)
    response.raise_for_status()

    all_lines: list[str] = []
    with zipfile.ZipFile(io.BytesIO(response.content)) as archive:
        for name in archive.namelist():
            if name.endswith(".txt"):
                text = archive.read(name).decode("utf-8", errors="replace")
                all_lines.extend(text.splitlines())

    return "\n".join(all_lines[-tail_lines:])
