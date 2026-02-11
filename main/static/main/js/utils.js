/**
 * Shared utility functions for the main app JavaScript files.
 */

/**
 * Get a cookie value by name.
 * @param {string} name - Cookie name
 * @returns {string|null} Cookie value or null if not found
 */
export function getCookie(name) {
    const cookies = document.cookie.split(";");
    for (const cookie of cookies) {
        const [cookieName, cookieValue] = cookie.trim().split("=");
        if (cookieName === name) return cookieValue;
    }
    return null;
}
