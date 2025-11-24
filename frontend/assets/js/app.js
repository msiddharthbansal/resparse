/**
 * RESPARSE Frontend Application
 */

// DOM Elements
const searchForm = document.getElementById('searchForm');
const searchInput = document.getElementById('searchInput');
const searchBtn = document.getElementById('searchBtn');
const topNSelect = document.getElementById('topNSelect');
const useCacheCheckbox = document.getElementById('useCacheCheckbox');

const loadingSpinner = document.getElementById('loadingSpinner');
const errorMessage = document.getElementById('errorMessage');
const errorText = document.getElementById('errorText');

const searchSummary = document.getElementById('searchSummary');
const summaryQuery = document.getElementById('summaryQuery');
const summaryCategories = document.getElementById('summaryCategories');
const resultCount = document.getElementById('resultCount');
const candidateCount = document.getElementById('candidateCount');

const resultsContainer = document.getElementById('resultsContainer');
const noResults = document.getElementById('noResults');
const noResultsMessage = document.getElementById('noResultsMessage');
const scholarLinkBtn = document.getElementById('scholarLinkBtn');

const exampleQueriesBtn = document.getElementById('exampleQueriesBtn');
const exampleQueries = document.getElementById('exampleQueries');
const exampleQueryBtns = document.querySelectorAll('.example-query-btn');

const aboutBtn = document.getElementById('aboutBtn');
const aboutModal = document.getElementById('aboutModal');
const closeModalBtn = document.getElementById('closeModalBtn');
const tryAgainBtn = document.getElementById('tryAgainBtn');

// State
let currentResults = null;

/**
 * Initialize application
 */
function init() {
    // Event listeners
    searchForm.addEventListener('submit', handleSearch);
    exampleQueriesBtn.addEventListener('click', toggleExampleQueries);
    exampleQueryBtns.forEach(btn => {
        btn.addEventListener('click', () => fillExampleQuery(btn.textContent));
    });
    aboutBtn.addEventListener('click', () => showModal());
    closeModalBtn.addEventListener('click', () => hideModal());
    tryAgainBtn.addEventListener('click', () => {
        hideNoResults();
        searchInput.focus();
    });

    // Close modal on outside click
    aboutModal.addEventListener('click', (e) => {
        if (e.target === aboutModal) hideModal();
    });

    // Check API health on load
    checkApiHealth();
}

/**
 * Check API health status
 */
async function checkApiHealth() {
    try {
        const health = await api.healthCheck();
        console.log('API Health:', health);
    } catch (error) {
        console.warn('API health check failed:', error);
    }
}

/**
 * Handle search form submission
 */
async function handleSearch(e) {
    e.preventDefault();
    
    const query = searchInput.value.trim();
    const topN = parseInt(topNSelect.value);
    const useCache = useCacheCheckbox.checked;

    if (!query) {
        showError('Please enter a search query');
        return;
    }

    // Hide previous results
    hideError();
    hideResults();
    hideNoResults();
    showLoading();

    try {
        // Perform search
        const results = await api.search(query, topN, useCache);
        currentResults = results;

        hideLoading();

        if (results.results && results.results.length > 0) {
            displayResults(results);
        } else {
            showNoResults(results.message, results.fallback_url);
        }

    } catch (error) {
        hideLoading();
        showError(error.message || 'Search failed. Please try again.');
    }
}

/**
 * Display search results
 */
function displayResults(data) {
    // Update summary
    summaryQuery.textContent = data.query;
    resultCount.textContent = data.results.length;
    candidateCount.textContent = `from ${data.total_candidates} evaluated papers`;
    
    // Display categories
    summaryCategories.innerHTML = data.categories.map(cat => `
        <span class="px-3 py-1 bg-purple-100 text-purple-700 rounded-full text-sm font-medium">
            ${cat.category_name} (${(cat.confidence * 100).toFixed(0)}%)
        </span>
    `).join('');

    searchSummary.classList.remove('hidden');
    searchSummary.classList.add('fade-in');

    // Display papers
    resultsContainer.innerHTML = data.results.map((paper, index) => createPaperCard(paper, index)).join('');
    resultsContainer.classList.remove('hidden');
    resultsContainer.classList.add('fade-in');

    // Scroll to results
    setTimeout(() => {
        searchSummary.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }, 100);
}

/**
 * Create paper card HTML
 */
function createPaperCard(paper, index) {
    const quartileColor = getQuartileColor(paper.journal.quartile);
    const finalScore = (paper.scores.final * 100).toFixed(1);

    return `
        <div class="paper-card bg-white rounded-xl shadow-lg p-6 mb-6 border-l-4 ${quartileColor}" style="animation-delay: ${index * 0.1}s">
            <!-- Rank Badge -->
            <div class="flex items-start justify-between mb-4">
                <div class="flex items-center gap-3">
                    <div class="flex-shrink-0 w-12 h-12 bg-gradient-to-br from-blue-500 to-purple-600 rounded-lg flex items-center justify-center text-white font-bold text-xl">
                        ${paper.rank}
                    </div>
                    <div>
                        <h3 class="text-xl font-bold text-gray-800 hover:text-blue-600 transition cursor-pointer" onclick="toggleAbstract(${paper.paper_id})">
                            ${paper.title}
                        </h3>
                        <p class="text-sm text-gray-500 mt-1">
                            ${paper.authors.slice(0, 3).map(a => a.name).join(', ')}
                            ${paper.authors.length > 3 ? ` <span class="text-gray-400">et al.</span>` : ''}
                        </p>
                    </div>
                </div>
                <div class="flex gap-2">
                    ${paper.doi ? `<a href="https://doi.org/${paper.doi}" target="_blank" class="text-blue-600 hover:text-blue-700 transition" title="View DOI">
                        <i class="fas fa-external-link-alt"></i>
                    </a>` : ''}
                    ${paper.pdf_url ? `<a href="${paper.pdf_url}" target="_blank" class="text-red-600 hover:text-red-700 transition" title="View PDF">
                        <i class="fas fa-file-pdf"></i>
                    </a>` : ''}
                </div>
            </div>

            <!-- Journal Info -->
            <div class="bg-gray-50 rounded-lg p-4 mb-4">
                <div class="flex flex-wrap items-center gap-4">
                    <div class="flex items-center gap-2">
                        <i class="fas fa-book text-blue-600"></i>
                        <span class="font-semibold text-gray-800">${paper.journal.name}</span>
                    </div>
                    <span class="px-3 py-1 ${quartileColor} rounded-full text-sm font-bold">
                        ${paper.journal.quartile}
                    </span>
                    <span class="text-sm text-gray-600">
                        <i class="fas fa-chart-line text-green-600 mr-1"></i>
                        JIF: ${paper.journal.jif.toFixed(1)}
                    </span>
                    ${paper.journal.ranking ? `
                    <span class="text-sm text-gray-600">
                        <i class="fas fa-trophy text-yellow-600 mr-1"></i>
                        Rank #${paper.journal.ranking}
                    </span>` : ''}
                    <span class="text-sm text-gray-600">
                        <i class="fas fa-calendar text-purple-600 mr-1"></i>
                        ${paper.publication.year}
                    </span>
                    ${paper.citation_count > 0 ? `
                    <span class="text-sm text-gray-600">
                        <i class="fas fa-quote-right text-orange-600 mr-1"></i>
                        ${paper.citation_count} citations
                    </span>` : ''}
                </div>
            </div>

            <!-- Explanation -->
            <div class="bg-blue-50 border-l-4 border-blue-400 p-4 mb-4 rounded">
                <div class="flex items-start">
                    <i class="fas fa-lightbulb text-blue-600 text-xl mr-3 mt-1"></i>
                    <div>
                        <p class="font-semibold text-gray-800 mb-1">Why this paper?</p>
                        <p class="text-gray-700 text-sm leading-relaxed">${paper.explanation}</p>
                    </div>
                </div>
            </div>

            <!-- Overall Score -->
            <div class="mb-4 pt-2 border-t border-gray-200">
                <div class="flex justify-between items-center">
                    <span class="font-semibold text-gray-800">
                        <i class="fas fa-star text-yellow-500 mr-1"></i>
                        Overall Score
                    </span>
                    <span class="text-2xl font-bold text-blue-600">${finalScore}%</span>
                </div>
            </div>

            <!-- Abstract (Collapsible) -->
            <div id="abstract-${paper.paper_id}" class="hidden mt-4 pt-4 border-t border-gray-200">
                <p class="font-semibold text-gray-800 mb-2">
                    <i class="fas fa-file-alt text-gray-600 mr-2"></i>
                    Abstract
                </p>
                <p class="text-gray-700 text-sm leading-relaxed">${paper.abstract}</p>
                
                ${paper.keywords ? `
                <div class="mt-4">
                    <p class="text-sm font-semibold text-gray-700 mb-2">Keywords:</p>
                    <div class="flex flex-wrap gap-2">
                        ${paper.keywords.split(',').map(kw => `
                            <span class="px-2 py-1 bg-gray-100 text-gray-700 rounded text-xs">
                                ${kw.trim()}
                            </span>
                        `).join('')}
                    </div>
                </div>` : ''}

                <div class="mt-4 flex flex-wrap gap-3">
                    ${paper.doi ? `
                    <a href="https://doi.org/${paper.doi}" target="_blank" 
                       class="inline-flex items-center px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition text-sm font-medium">
                        <i class="fas fa-link mr-2"></i>
                        View Paper (DOI)
                    </a>` : ''}
                    ${paper.pdf_url ? `
                    <a href="${paper.pdf_url}" target="_blank" 
                       class="inline-flex items-center px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-lg transition text-sm font-medium">
                        <i class="fas fa-file-pdf mr-2"></i>
                        Download PDF
                    </a>` : ''}
                    <button onclick="copyBibtex('${paper.paper_id}')" 
                            class="inline-flex items-center px-4 py-2 bg-gray-600 hover:bg-gray-700 text-white rounded-lg transition text-sm font-medium">
                        <i class="fas fa-copy mr-2"></i>
                        Copy Citation
                    </button>
                </div>
            </div>

            <!-- Toggle Abstract Button -->
            <button onclick="toggleAbstract(${paper.paper_id})" 
                    class="w-full mt-4 py-2 text-blue-600 hover:text-blue-700 font-medium text-sm transition flex items-center justify-center gap-2">
                <span id="abstract-toggle-${paper.paper_id}">
                    <i class="fas fa-chevron-down"></i> Show Abstract
                </span>
            </button>
        </div>
    `;
}

/**
 * Toggle abstract visibility
 */
function toggleAbstract(paperId) {
    const abstractDiv = document.getElementById(`abstract-${paperId}`);
    const toggleBtn = document.getElementById(`abstract-toggle-${paperId}`);
    
    if (abstractDiv.classList.contains('hidden')) {
        abstractDiv.classList.remove('hidden');
        abstractDiv.classList.add('slide-down');
        toggleBtn.innerHTML = '<i class="fas fa-chevron-up"></i> Hide Abstract';
    } else {
        abstractDiv.classList.add('hidden');
        toggleBtn.innerHTML = '<i class="fas fa-chevron-down"></i> Show Abstract';
    }
}

/**
 * Copy BibTeX citation
 */
function copyBibtex(paperId) {
    const paper = currentResults.results.find(p => p.paper_id === paperId);
    if (!paper) return;

    const authors = paper.authors.map(a => a.name).join(' and ');
    const bibtex = `@article{${paper.doi || `paper_${paperId}`},
  title={${paper.title}},
  author={${authors}},
  journal={${paper.journal.name}},
  year={${paper.publication.year}},
  volume={${paper.publication.volume}},
  ${paper.doi ? `doi={${paper.doi}},` : ''}
  ${paper.journal.jif ? `note={Impact Factor: ${paper.journal.jif}}` : ''}
}`;

    // Copy to clipboard
    navigator.clipboard.writeText(bibtex).then(() => {
        // Show temporary notification
        showNotification('Citation copied to clipboard!');
    }).catch(err => {
        console.error('Failed to copy:', err);
        showNotification('Failed to copy citation', 'error');
    });
}

/**
 * Get quartile color class
 */
function getQuartileColor(quartile) {
    switch(quartile) {
        case 'Q1':
            return 'border-green-500 bg-green-50';
        case 'Q2':
            return 'border-blue-500 bg-blue-50';
        case 'Q3':
            return 'border-yellow-500 bg-yellow-50';
        case 'Q4':
            return 'border-orange-500 bg-orange-50';
        default:
            return 'border-gray-500 bg-gray-50';
    }
}

/**
 * Toggle example queries visibility
 */
function toggleExampleQueries() {
    exampleQueries.classList.toggle('hidden');
}

/**
 * Fill search input with example query
 */
function fillExampleQuery(query) {
    searchInput.value = query;
    exampleQueries.classList.add('hidden');
    searchInput.focus();
}

/**
 * Show loading spinner
 */
function showLoading() {
    loadingSpinner.classList.remove('hidden');
    loadingSpinner.classList.add('fade-in');
    searchBtn.disabled = true;
    searchBtn.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i> Searching...';
}

/**
 * Hide loading spinner
 */
function hideLoading() {
    loadingSpinner.classList.add('hidden');
    searchBtn.disabled = false;
    searchBtn.innerHTML = '<i class="fas fa-search"></i> <span>Search</span>';
}

/**
 * Show error message
 */
function showError(message) {
    errorText.textContent = message;
    errorMessage.classList.remove('hidden');
    errorMessage.classList.add('fade-in');
    errorMessage.scrollIntoView({ behavior: 'smooth', block: 'center' });
}

/**
 * Hide error message
 */
function hideError() {
    errorMessage.classList.add('hidden');
}

/**
 * Show no results message
 */
function showNoResults(message, fallbackUrl) {
    if (message) {
        noResultsMessage.textContent = message;
    } else {
        noResultsMessage.textContent = 'Try different keywords or broader search terms';
    }

    if (fallbackUrl) {
        scholarLinkBtn.href = fallbackUrl;
        scholarLinkBtn.classList.remove('hidden');
    } else {
        scholarLinkBtn.classList.add('hidden');
    }

    noResults.classList.remove('hidden');
    noResults.classList.add('fade-in');
}

/**
 * Hide no results message
 */
function hideNoResults() {
    noResults.classList.add('hidden');
    scholarLinkBtn.classList.add('hidden');
}

/**
 * Hide results
 */
function hideResults() {
    resultsContainer.classList.add('hidden');
    searchSummary.classList.add('hidden');
}

/**
 * Show about modal
 */
function showModal() {
    aboutModal.classList.remove('hidden');
    aboutModal.classList.add('fade-in');
}

/**
 * Hide about modal
 */
function hideModal() {
    aboutModal.classList.add('hidden');
}

/**
 * Show notification toast
 */
function showNotification(message, type = 'success') {
    const notification = document.createElement('div');
    notification.className = `fixed bottom-4 right-4 px-6 py-4 rounded-lg shadow-2xl z-50 fade-in ${
        type === 'success' ? 'bg-green-500' : 'bg-red-500'
    } text-white font-medium flex items-center gap-2`;
    
    notification.innerHTML = `
        <i class="fas ${type === 'success' ? 'fa-check-circle' : 'fa-exclamation-circle'}"></i>
        ${message}
    `;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.remove();
    }, 3000);
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', init);

// Keyboard shortcuts
document.addEventListener('keydown', (e) => {
    // Ctrl/Cmd + K to focus search
    if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault();
        searchInput.focus();
    }
    
    // Escape to close modal
    if (e.key === 'Escape' && !aboutModal.classList.contains('hidden')) {
        hideModal();
    }
});
