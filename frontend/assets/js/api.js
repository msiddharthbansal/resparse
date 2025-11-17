/**
 * API Client for RESPARSE Backend
 */

const API_BASE_URL = 'http://localhost:8000/api';

class ResparseAPI {
    constructor(baseUrl = API_BASE_URL) {
        this.baseUrl = baseUrl;
    }

    /**
     * Search for research papers
     * @param {string} query - Search query
     * @param {number} topN - Number of results
     * @param {boolean} useCache - Whether to use cache
     * @returns {Promise<Object>} Search results
     */
    async search(query, topN = 10, useCache = true) {
        try {
            const response = await fetch(`${this.baseUrl}/search`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    query: query,
                    top_n: topN,
                    use_cache: useCache
                })
            });

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.detail || 'Search failed');
            }

            return await response.json();
        } catch (error) {
            console.error('Search error:', error);
            throw error;
        }
    }

    /**
     * Get paper details by ID
     * @param {number} paperId - Paper ID
     * @returns {Promise<Object>} Paper details
     */
    async getPaperDetails(paperId) {
        try {
            const response = await fetch(`${this.baseUrl}/papers/${paperId}`);
            
            if (!response.ok) {
                throw new Error('Failed to fetch paper details');
            }

            return await response.json();
        } catch (error) {
            console.error('Paper details error:', error);
            throw error;
        }
    }

    /**
     * Get all available categories
     * @returns {Promise<Object>} Categories list
     */
    async getCategories() {
        try {
            const response = await fetch(`${this.baseUrl}/categories`);
            
            if (!response.ok) {
                throw new Error('Failed to fetch categories');
            }

            return await response.json();
        } catch (error) {
            console.error('Categories error:', error);
            throw error;
        }
    }

    /**
     * Check system health
     * @returns {Promise<Object>} Health status
     */
    async healthCheck() {
        try {
            const response = await fetch(`${this.baseUrl}/health`);
            
            if (!response.ok) {
                throw new Error('Health check failed');
            }

            return await response.json();
        } catch (error) {
            console.error('Health check error:', error);
            throw error;
        }
    }
}

// Export API instance
const api = new ResparseAPI();
