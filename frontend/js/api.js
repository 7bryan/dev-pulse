// base backend url
const BACKEND_URL = "http://localhost:8000";

// shared request helper: parses JSON either way and throws a readable
// error (using the backend's "detail" message) when the response isn't ok
async function apiRequest(path) {
  const response = await fetch(`${BACKEND_URL}${path}`);

  let payload = null;
  try {
    payload = await response.json();
  } catch (_) {
    // no/invalid JSON body, payload stays null
  }

  if (!response.ok) {
    const message =
      (payload && payload.detail) || `Request failed (${response.status})`;
    throw new Error(message);
  }

  return payload;
}

async function checkBackendHealth() {
  const badge = document.getElementById("api-status-badge");
  const statusText = document.getElementById("status-text");

  try {
    await apiRequest("/health");
    badge.className = "status-badge online";
    statusText.innerText = "Backend connected";
    return true;
  } catch (error) {
    badge.className = "status-badge offline";
    statusText.innerText = "Backend offline";
    return false;
  }
}

// fetching each feature

function getUser(username) {
  return apiRequest(`/github/${encodeURIComponent(username)}`);
}

function getUserRepos(username) {
  return apiRequest(`/github/${encodeURIComponent(username)}/repos`);
}

function getUserActivity(username) {
  return apiRequest(`/github/${encodeURIComponent(username)}/activity`);
}

function getRepo(username, repo) {
  return apiRequest(
    `/github/${encodeURIComponent(username)}/repos/${encodeURIComponent(repo)}`,
  );
}

function getRepoIssues(username, repo) {
  return apiRequest(
    `/github/${encodeURIComponent(username)}/repos/${encodeURIComponent(repo)}/issues`,
  );
}

function getRepoCommits(username, repo) {
  return apiRequest(
    `/github/${encodeURIComponent(username)}/repos/${encodeURIComponent(repo)}/commits`,
  );
}

function getRepoContributors(username, repo) {
  return apiRequest(
    `/github/${encodeURIComponent(username)}/repos/${encodeURIComponent(repo)}/contributors`,
  );
}

function getRepoBranches(username, repo) {
  return apiRequest(
    `/github/${encodeURIComponent(username)}/repos/${encodeURIComponent(repo)}/branches`,
  );
}
