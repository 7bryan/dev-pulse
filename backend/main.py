# import httpx   note: remove it because already decoupling
from fastapi import FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from services import (
    GithubAuthError,
    GithubConnectionError,
    GithubRateLimitError,
    GithubServerError,
    fetch_github_data,
    fetch_user_activity,
    fetch_user_repo_branches,
    fetch_user_repo_commits,
    fetch_user_repo_contributors,
    fetch_user_repo_data,
    fetch_user_repo_issues,
    fetch_user_repos,
)

app = FastAPI(title="Github User Proxy Services")

# defining allowed origins
origins = [
    "http://localhost:3000",
]

# condigure CORS so the frontend can talk to the backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # allowed domains
    allow_credentials=True,
    allow_methods=["*"],  # allow all standard http method (GET, POST, etc)
    allow_headers=["*"],  # allow all custom or standard request headers
)


# global exception handlers for translating service-layer exceptions
# into HTTP responses


# convert service-layer rate limit exceptions into HTTP responses
@app.exception_handler(GithubRateLimitError)
async def handle_rate_limit_error(request: Request, exc: GithubRateLimitError):
    return JSONResponse(
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        content={
            "success": False,
            "detail": "Rate limit exceeded. Please try again later",
        },
    )


# catching internal server error
@app.exception_handler(GithubServerError)
async def handle_server_error(request: Request, exc: GithubServerError):
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"success": False, "detail": "An unexpected error occurred"},
    )


@app.exception_handler(GithubAuthError)
async def handle_auth_error(request: Request, exc: GithubAuthError):
    return JSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED,
        content={
            "success": False,
            "detail": "Authentication failed",
        },
    )


@app.exception_handler(GithubConnectionError)
async def handle_connection_error(request: Request, exc: GithubConnectionError):
    return JSONResponse(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        content={
            "success": False,
            "detail": "Service temporarily unavailable",
        },
    )


# API endpoints
@app.get("/github/{username}")
async def get_github_user(username: str):
    # endpoint that accept a username, triggers the services layer
    # and handles the parsed json results

    # await async function from services.py
    data = await fetch_github_data(username)

    # if Github returned a 404 or something went wrong , data will be None
    if data is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Github user '{username}' not found",
        )

    # return the parsed dictionary. FastAPI convert it to JSON automatically
    return data


@app.get("/github/{username}/activity")
async def get_user_github_activity(username: str):
    # user-level recent public activity: pushes, issues, PRs, stars, forks etc
    data = await fetch_user_activity(username)

    if data is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Github user '{username}' not found",
        )

    return data


@app.get("/github/{username}/repos")
async def get_user_github_repos(username: str):
    data = await fetch_user_repos(username)

    if data is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Github user '{username}' not found or don't have any repo",
        )

    return data


@app.get("/github/{username}/repos/{repo}")
async def get_user_github_repo_data(username: str, repo: str):
    data = await fetch_user_repo_data(username, repo)

    if data is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Repository '{repo}' not found",
        )

    return data


@app.get("/github/{username}/repos/{repo}/issues")
async def get_user_github_repo_issues(username: str, repo: str):
    # repo_data = await fetch_user_repo_data(username, repo)

    # if not repo_data["has_issues"]:
    #     return {"status": "This repo don't have issues"}

    data = await fetch_user_repo_issues(username, repo)

    if data is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No Issues found or repository not found",
        )

    return data


@app.get("/github/{username}/repos/{repo}/commits")
async def get_user_github_repo_commits(username: str, repo: str):
    data = await fetch_user_repo_commits(username, repo)

    if data is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"something wrong {data}",
        )

    return data


@app.get("/github/{username}/repos/{repo}/contributors")
async def get_user_github_repo_contributors(username: str, repo: str):
    data = await fetch_user_repo_contributors(username, repo)

    if data is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"something wrong {data}",
        )

    return data


@app.get("/github/{username}/repos/{repo}/branches")
async def get_user_github_repo_branches(username: str, repo: str):
    data = await fetch_user_repo_branches(username, repo)

    if data is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"something wrong {data}",
        )

    return data


# a separate base point to test if the server is working
@app.get("/")
def read_root():
    return {"status": "success", "message": "FastAPI application is running"}


@app.get("/health")
def health_check():
    return {"status": "ok"}
