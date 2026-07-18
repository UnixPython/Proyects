import requests
from typing import Any


def get_job_token_scope(private_token: str, project_id1: int, project_id2: int) -> tuple[dict, dict]:
    
    url1 = f"https://gitlab.com/api/v4/projects/{project_id1}/job_token_scope"
    url2 = f"https://gitlab.com/api/v4/projects/{project_id2}/job_token_scope"

    headers = {
        "PRIVATE-TOKEN": private_token
    }

    r1 = requests.get(url1, headers=headers)
    r1.raise_for_status()

    r2 = requests.get(url2, headers=headers)
    r2.raise_for_status()

    data1: dict[str, Any] = r1.json()
    data2: dict[str, Any] = r2.json()

    print(f"Proyecto 1: {data1['inbound_enabled']}")
    print(f"Proyecto 2: {data2['inbound_enabled']}")
    return data1, data2


def get_job_info(job_token: str) -> dict:
    url = (
        "https://gitlab.com/api/v4/job"
    )

    headers = {
        "User-Agent": "README.MD",
        "JOB-TOKEN": job_token,
    }

    r = requests.get(url, headers=headers)
    r.raise_for_status()

    data: dict[str, Any] = r.json()
    print(data)
    return data

def add_to_allowlist(private_token: str, project_id: int, target_id: int) -> None:
    target_url = (
        f"https://gitlab.com/api/v4/projects/"
        f"{project_id}/job_token_scope/allowlist"
    )

    payload = {
        "target_project_id": target_id
    }

    headers = {
        "PRIVATE-TOKEN": private_token
    }

    r = requests.post(target_url, headers=headers, json=payload)
    r.raise_for_status()

    if r.status_code == 201:
        print("Proyecto añadido exitosamente.")


def remove_from_allowlist(
    private_token: str,
    project_id: int,
    target_id: int,
) -> None:
    headers = {
        "PRIVATE-TOKEN": private_token
    }

    url = (
        f"https://gitlab.com/api/v4/projects/"
        f"{project_id}/job_token_scope/allowlist/{target_id}"
    )

    response = requests.delete(url, headers=headers)
    response.raise_for_status()

    if response.status_code == 204:
        print("Proyecto eliminado exitosamente.")


def try_cross_project_access(job_token, target_project_id) -> dict:
    url = f"https://gitlab.com/api/v4/projects/{target_project_id}/repository/files/README.md/raw?ref=main"
    headers = {"JOB-TOKEN": job_token}
    r = requests.get(url, headers=headers)
    r.raise_for_status()
    data = r.text
    print(data)
    return {}

