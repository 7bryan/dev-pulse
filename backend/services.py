from typing import Any, Dict, Optional

import httpx


# custom exception for better code readbility and stucture
class GithubError(Exception):
    # base exception for all Github API Errors
    pass


# using inheritance for cleaner code
class GithubRateLimitError(GithubError):
    # raised when too many request (429)
    pass


class GithubAuthError(GithubError):
    # raised when unauthorized (401)
    pass


class GithubServerError(GithubError):
    # raised when the internal server is error (500)
    pass


class GithubConnectionError(GithubError):
    # catching connection error
    pass


HEADERS = {"User-Agent": "Awecome-Octocat-App"}


async def request_github(url):
    try:
        # using httpx.AsyncClient for non blocking networks calls (asynchronous)
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=HEADERS)

            if response.status_code != 200:
                # raise HTTPStatusError if one occurred
                response.raise_for_status()

            return response.json()

    # instead of using print, raise an exception or handle it via a status indicator
    # raise httpx.HTTPStatusError(
    #     "Too many requests to Github API",
    #     request=response.request,
    #     response=response,
    # )
    except httpx.HTTPStatusError as e:
        status = e.response.status_code

        if status == 429:
            raise GithubRateLimitError("Too many requests to Github API") from e
        elif status in (401, 403):
            raise GithubAuthError(
                f"Aunthentication failed ({status}): Not Allowed"
            ) from e
        elif status == 404:
            return None
        # handling multiple server side erro
        elif 500 <= status < 600:
            raise GithubServerError("Github had an internal problem")
        # handling unknown error or handling unexpected github error
        else:
            print("Unknown Github Error")
            return None

    except httpx.RequestError as e:
        # catching connection errors, timeout, etc. safely
        raise GithubConnectionError("Network error occurr") from e
        # return None


async def fetch_github_data(username: str) -> Optional[Dict[str, Any]]:
    url = f"https://api.github.com/users/{username}"

    return await request_github(url)


async def fetch_user_repos(username: str) -> Optional[Dict[str, Any]]:
    # getting all repo of <username>
    url = f"https://api.github.com/users/{username}/repos"

    return await request_github(url)


async def fetch_user_repo_data(username: str, repo: str) -> Optional[Dict[str, Any]]:
    url = f"https://api.github.com/repos/{username}/{repo}"

    return await request_github(url)


# for getting data of repo issues
async def fetch_user_repo_issues(username: str, repo: str) -> Optional[Dict[str, Any]]:
    # base url for getting a repo issues of target username
    url = f"https://api.github.com/repos/{username}/{repo}/issues"

    return await request_github(url)


# retrun commits of the user repo
async def fetch_user_repo_commits(username: str, repo: str) -> Optional[Dict[str, Any]]:
    url = f"https://api.github.com/repos/{username}/{repo}/commits"

    return await request_github(url)


# service for getting contributors of a repo
async def fetch_user_repo_contributors(
    username: str, repo: str
) -> Optional[Dict[str, Any]]:
    url = f"https://api.github.com/repos/{username}/{repo}/contributors"

    return await request_github(url)


# getting a repo branches
async def fetch_user_repo_branches(
    username: str, repo: str
) -> Optional[Dict[str, Any]]:
    url = f"https://api.github.com/repos/{username}/{repo}/branches"

    return await request_github(url)


# recent public activity for a user (pushes, issues, PRs, stars, forks, etc)
# this is user-level, unlike everything above which is scoped to one repo
async def fetch_user_activity(username: str) -> Optional[Dict[str, Any]]:
    url = f"https://api.github.com/users/{username}/events/public"

    return await request_github(url)
