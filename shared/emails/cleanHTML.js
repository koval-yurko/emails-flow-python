
export function cleanHTML(htmlString, options = {}) {
    const {
        removeComments = true,
        removeEmptyElements = true,
        preserveStructure = false,
        extractTextOnly = false
    } = options;

    htmlString = htmlString.replace(`/\r?\n|\r/g, ''`); // Remove new lines

    if (extractTextOnly) {
        return extractTextContent(htmlString);
    }

    return cleanHTMLContent(htmlString, {
        removeComments,
        removeEmptyElements,
        preserveStructure
    });
}

function extractTextContent(html) {
    // Handle Node.js environment without DOM
    if (typeof document === 'undefined') {
        // Use JSDOM in Node.js environment
        const { JSDOM } = require('jsdom');
        const dom = new JSDOM();
        const tempDiv = dom.window.document.createElement('div');
        tempDiv.innerHTML = html;
        return extractTextFromElement(tempDiv);
    }

    // Create a temporary DOM element to parse HTML
    const tempDiv = document.createElement('div');
    tempDiv.innerHTML = html;

    return extractTextFromElement(tempDiv);
}

function extractTextFromElement(tempDiv) {
    // Remove script and style elements
    const scriptsAndStyles = tempDiv.querySelectorAll('script, style');
    scriptsAndStyles.forEach(el => el.remove());

    // Remove hidden elements
    const hiddenElements = tempDiv.querySelectorAll('[style*="display:none"], [style*="visibility:hidden"]');
    hiddenElements.forEach(el => el.remove());

    // Get text content and clean it up
    let textContent = tempDiv.textContent || tempDiv.innerText || '';

    // Clean up whitespace and formatting
    textContent = textContent
        .replace(/\s+/g, ' ')           // Replace multiple whitespace with single space
        .replace(/\n\s*\n/g, '\n\n')    // Preserve paragraph breaks
        .replace(/^\s+|\s+$/gm, '')     // Remove leading/trailing spaces from lines
        .trim();

    return textContent;
}

function cleanHTMLContent(html, options) {
    let cleaned = html;

    // Remove all style attributes
    cleaned = cleaned.replace(/\s*style\s*=\s*["'][^"']*["']/gi, '');

    // Remove all class attributes
    cleaned = cleaned.replace(/\s*class\s*=\s*["'][^"']*["']/gi, '');

    // Remove all id attributes (except if preserving structure)
    if (!options.preserveStructure) {
        cleaned = cleaned.replace(/\s*id\s*=\s*["'][^"']*["']/gi, '');
    }

    // Remove inline CSS and style tags
    cleaned = cleaned.replace(/<style[^>]*>[\s\S]*?<\/style>/gi, '');

    // Remove script tags
    cleaned = cleaned.replace(/<script[^>]*>[\s\S]*?<\/script>/gi, '');

    // Remove comments
    if (options.removeComments) {
        cleaned = cleaned.replace(/<!--[\s\S]*?-->/g, '');
    }

    // Remove tracking and analytics attributes
    cleaned = cleaned.replace(/\s*(onclick|onload|onmouseover|onmouseout|data-[^=]*)\s*=\s*["'][^"']*["']/gi, '');

    // Remove table presentation attributes
    cleaned = cleaned.replace(/\s*(cellpadding|cellspacing|border|align|valign|width|height|bgcolor)\s*=\s*["'][^"']*["']/gi, '');

    // Remove font and color attributes
    cleaned = cleaned.replace(/\s*(color|face|size)\s*=\s*["'][^"']*["']/gi, '');

    // Remove target="_blank" and tracking attributes from links
    cleaned = cleaned.replace(/\s*(target|rel)\s*=\s*["'][^"']*["']/gi, '');

    // // Clean up tracking URLs (decode and extract actual URLs)
    // cleaned = cleaned.replace(/href\s*=\s*["']https:\/\/tracking\.[^"']*\/(CL0\/)?([^"']*?)["']/gi,
    //     (match, p1, url) => {
    //         try {
    //             const decodedUrl = decodeURIComponent(url);
    //             return `href="${decodedUrl}"`;
    //         } catch (e) {
    //             return `href="${url}"`;
    //         }
    //     }
    // );

    // Remove image tracking pixels
    cleaned = cleaned.replace(/<img[^>]*tracking[^>]*>/gi, '');

    // Remove empty attributes
    cleaned = cleaned.replace(/\s*=\s*["']["']/g, '');

    // Clean up multiple spaces
    cleaned = cleaned.replace(/\s+/g, ' ');

    if (options.removeEmptyElements) {
        // Remove empty elements (preserve self-closing tags)
        cleaned = cleaned.replace(/<(?!br|hr|img|input|meta|link|area|base|col|embed|source|track|wbr)([a-zA-Z][a-zA-Z0-9]*)[^>]*>\s*<\/\1>/gi, '');
    }

    // Format the output
    cleaned = formatHTML(cleaned);

    return cleaned;
}

function formatHTML(html) {
    // Basic HTML formatting for readability
    return html
        .replace(/></g, '>\n<')
        .replace(/^\s+|\s+$/gm, '')
        .split('\n')
        .filter(line => line.trim() !== '')
        .join('\n');
}

function removeAllStyles(element) {
    // Remove styles from a DOM element and all its children
    if (element.removeAttribute) {
        element.removeAttribute('style');
        element.removeAttribute('class');
    }

    // Recursively clean child elements
    if (element.children) {
        for (let child of element.children) {
            removeAllStyles(child);
        }
    }
}

