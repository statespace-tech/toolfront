// Simple analytics for ToolFront docs - tracks what people actually use
document.addEventListener('DOMContentLoaded', function() {
    // Only run if gtag is available
    if (typeof gtag === 'undefined') return;
    
    // Track which database/AI model pages are viewed
    const path = window.location.pathname;
    let contentType = null;
    let contentName = null;
    
    if (path.includes('/databases/')) {
        contentType = 'database';
        contentName = path.split('/databases/')[1].replace(/\.(html|md)$/, '');
    } else if (path.includes('/ai_models/')) {
        contentType = 'ai_model';
        contentName = path.split('/ai_models/')[1].replace(/\.(html|md)$/, '');
    } else if (path.includes('/examples/')) {
        contentType = 'example';
        contentName = path.split('/examples/')[1].replace(/\.(html|md)$/, '');
    }
    
    if (contentType && contentName) {
        gtag('event', 'content_view', {
            'content_type': contentType,
            'content_name': contentName,
            'page_path': path
        });
    }
    
    // Track section views (which parts of docs are most useful)
    const section = path.split('/')[1] || 'home';
    gtag('event', 'section_view', {
        'section_name': section,
        'page_title': document.title
    });
    
    // Track searches to understand what's missing/hard to find
    const searchInput = document.querySelector('.md-search__input');
    if (searchInput) {
        let searchTimer;
        searchInput.addEventListener('input', function(e) {
            clearTimeout(searchTimer);
            searchTimer = setTimeout(function() {
                if (e.target.value.length > 3) {
                    gtag('event', 'search', {
                        'search_term': e.target.value
                    });
                }
            }, 1500); // Only track if user pauses typing
        });
    }
    
    // Track code copying to see what integrations people are building
    document.addEventListener('click', function(e) {
        if (e.target.closest('.md-clipboard')) {
            const codeBlock = e.target.closest('.highlight');
            const heading = findPreviousHeading(codeBlock);
            
            gtag('event', 'code_copy', {
                'page_section': heading ? heading.textContent : 'unknown',
                'page_path': path
            });
        }
    });
    
    function findPreviousHeading(element) {
        if (!element) return null;
        let current = element.previousElementSibling;
        while (current) {
            if (current.tagName && current.tagName.match(/^H[1-6]$/)) {
                return current;
            }
            current = current.previousElementSibling;
        }
        return null;
    }
});