/**
 * Hide label filter from search input when using label URLs
 */
function hideLabelFilter() {
    console.log('Attempting to hide label filter');
    // Find the search textarea and remove the label filter from it
    var searchTextarea = document.querySelector('#id_q');
    if (searchTextarea) {
        console.log('Found search textarea, current value:', searchTextarea.value);
        var currentValue = searchTextarea.value;
        // Remove label:"..." from the search query
        var labelPattern = /label:"[^"]*"/g;
        var cleanedValue = currentValue.replace(labelPattern, '').trim();
        // Remove extra spaces and clean up
        cleanedValue = cleanedValue.replace(/\s+/g, ' ');
        searchTextarea.value = cleanedValue;
        console.log('Cleaned textarea value:', cleanedValue);
        
        // Also clear the highlighted output display
        var highlightedOutput = document.querySelector('.highlighted-output');
        if (highlightedOutput) {
            console.log('Found highlighted output, clearing it');
            highlightedOutput.innerHTML = '';
            console.log('Cleared highlighted output');
        } else {
            console.log('Highlighted output not found');
        }
        
        // Trigger any change events that might be needed
        var event = new Event('input', { bubbles: true });
        searchTextarea.dispatchEvent(event);
        console.log('Triggered input event');
    } else {
        console.log('Search textarea not found');
    }
}

// Run when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    console.log('DOMContentLoaded - hideLabelFilter function loaded');
    // Check if we should hide the label filter by looking for the flag element
    var flagElement = document.getElementById('label-filter-flag');
    if (flagElement && flagElement.getAttribute('data-hide-label-filter') === 'true') {
        hideLabelFilter();
    }
});

// Also try after a short delay in case the input is populated dynamically
setTimeout(function() {
    console.log('Timeout - checking if label filter should be hidden');
    var flagElement = document.getElementById('label-filter-flag');
    if (flagElement && flagElement.getAttribute('data-hide-label-filter') === 'true') {
        hideLabelFilter();
    }
}, 100);
