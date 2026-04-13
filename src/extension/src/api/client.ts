export const API_BASE_URL = "http://localhost:8000/api/v1";

// Tokens are stored in chrome.storage.local which isolates them from untrusted sites
export async function getToken(): Promise<string | null> {
    if (!chrome?.storage) return null;
    const result = await chrome.storage.local.get(["auth_token"]);
    return (result.auth_token as string) || null;
}

export async function setToken(token: string): Promise<void> {
    if (!chrome?.storage) return;
    await chrome.storage.local.set({ auth_token: token });
}

export async function logout(): Promise<void> {
    if (!chrome?.storage) return;
    await chrome.storage.local.remove(["auth_token"]);
}

export async function fetchWithAuth(endpoint: string, options: RequestInit = {}) {
    const token = await getToken();
    const headers = new Headers(options.headers || {});
    
    if (token) {
        headers.set("Authorization", `Bearer ${token}`);
    }
    
    headers.set("Content-Type", "application/json");

    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
        ...options,
        headers
    });
    
    // Auto-remove token if unauthorized
    if (response.status === 401) {
        await logout();
        throw new Error("Unauthorized - Token Expired or Invalid");
    }
    
    if (!response.ok) {
        throw new Error(`API Request failed with status ${response.status}`);
    }
    
    return response.json();
}

export async function fetchUserData() {
    return fetchWithAuth("/users/me");
}

export async function getMasterResume() {
    return fetchWithAuth("/resumes/master");
}

export async function getResumeVersion(versionId: string) {
    return fetchWithAuth(`/resumes/versions/${versionId}`);
}

export async function getApplication(applicationId: string) {
    return fetchWithAuth(`/applications/${applicationId}`);
}

export async function getCredentialPassword(credentialId: string) {
    // Hits the new endpoint we just created in issue #17!
    const data = await fetchWithAuth(`/credentials/${credentialId}/reveal`);
    return data.password;
}
