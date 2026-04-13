import { describe, it, expect, vi, beforeEach } from 'vitest';
import { fetchUserData, getToken, setToken, logout, API_BASE_URL } from '../client';

const mockStorage = {
    get: vi.fn(),
    set: vi.fn(),
    remove: vi.fn()
};

(globalThis as any).chrome = {
    // Provide minimal mock for chrome object
    runtime: {},
    storage: {
        local: mockStorage
    }
};

describe('API Client Configuration', () => {
    beforeEach(() => {
        vi.clearAllMocks();
        globalThis.fetch = vi.fn();
    });

    it('should extract tokens from chrome storage', async () => {
        mockStorage.get.mockResolvedValue({ auth_token: 'test_token_123' });
        const token = await getToken();
        expect(token).toBe('test_token_123');
        expect(mockStorage.get).toHaveBeenCalledWith(['auth_token']);
    });

    it('should assign tokens via setToken natively', async () => {
        await setToken('new_token');
        expect(mockStorage.set).toHaveBeenCalledWith({ auth_token: 'new_token' });
    });

    it('should purge token on explicit logout', async () => {
        await logout();
        expect(mockStorage.remove).toHaveBeenCalledWith(['auth_token']);
    });

    it('should attach headers automatically and return parsed JSON upon successful fetch', async () => {
        mockStorage.get.mockResolvedValue({ auth_token: 'valid_token' });
        (globalThis.fetch as any).mockResolvedValue({
            ok: true,
            status: 200,
            json: async () => ({ email: 'test@demo.com' })
        });

        const user = await fetchUserData();
        expect(user.email).toBe('test@demo.com');
        
        // Ensure proper endpoint and headers
        expect(globalThis.fetch).toHaveBeenCalledWith(`${API_BASE_URL}/users/me`, expect.objectContaining({
            headers: expect.any(Headers)
        }));
    });
    
    it('should logout cleanly upon 401 Unauthorized API reject', async () => {
        mockStorage.get.mockResolvedValue({ auth_token: 'invalid_token' });
        (globalThis.fetch as any).mockResolvedValue({
            ok: false,
            status: 401
        });

        await expect(fetchUserData()).rejects.toThrow("Unauthorized - Token Expired or Invalid");
        expect(mockStorage.remove).toHaveBeenCalledWith(['auth_token']);
    });
});
