// Import the diff library
const diff = require('diff');
const { parsePatch, applyPatch } = diff;

// Define utility functions
function convertEscapeSequences(input) {
    // First convert escape sequences
    const withConvertedEscapes = input
        .replace(/\\n/g, '\n')   // Convert \n to actual newlines
        .replace(/\\t/g, '\t')   // Convert \t to actual tabs
        .replace(/\\r/g, '\r')   // Convert \r to actual carriage returns
        .replace(/\\\\/g, '\\')  // Convert \\ to single backslash
        .replace(/\\"/g, '"')    // Convert \" to double quote
        .replace(/\\'/g, "'");   // Convert \' to single quote

    // Then normalize line endings (convert \r\n to \n)
    return withConvertedEscapes.replace(/\r\n/g, '\n');
}

function preprocessDiff(diff) {
    // Split the diff into lines
    const lines = diff.split('\n');
    const processedLines = [];

    // Track if we're inside a hunk
    let insideHunk = false;

    // Process each line
    for (let i = 0; i < lines.length; i++) {
        const line = lines[i];

        // Check if this is a hunk header
        if (line.startsWith('@@')) {
            insideHunk = true;
            // Ensure there's a space after the hunk header
            if (line.endsWith('@@')) {
                processedLines.push(line + ' ');
            } else {
                processedLines.push(line);
            }
        }
        // If we're inside a hunk, ensure all lines have a prefix
        else if (insideHunk) {
            // If the line doesn't start with +, -, or space, add a space prefix
            if (line.length > 0 && !line.startsWith('+') && !line.startsWith('-') && !line.startsWith(' ')) {
                processedLines.push(' ' + line);
            } else {
                processedLines.push(line);
            }
        }
        // If we're not inside a hunk, just add the line as is
        else {
            processedLines.push(line);
        }
    }

    return processedLines.join('\n');
}

function applyDiffToContent(originalContent, diff) {
    // Convert escape sequences in the diff string
    const withEscapesConverted = convertEscapeSequences(diff);

    // Preprocess the diff to fix formatting issues
    const processedDiff = preprocessDiff(withEscapesConverted);

    try {
        // Parse the unified diff
        const patches = parsePatch(processedDiff);

        // Apply all patches
        let patchedContent = originalContent;
        for (const patch of patches) {
            try {
                const result = applyPatch(patchedContent, patch);
                if (result !== false) {
                    patchedContent = result;
                }
            } catch (patchErr) {
                console.error(`Error applying patch: ${patchErr.message}`);
            }
        }

        return patchedContent;
    } catch (err) {
        console.error(`Error parsing diff: ${err.message}`);
        return originalContent; // Return original content if there's an error
    }
}

// Test function to run all tests
function runTests() {
    console.log('Running diff utilities tests...');

    // Test convertEscapeSequences
    testConvertEscapeSequences();

    // Test preprocessDiff
    testPreprocessDiff();

    // Test applyDiffToContent
    testApplyDiffToContent();

    console.log('All tests completed!');
}

// Test convertEscapeSequences function
function testConvertEscapeSequences() {
    console.log('\nTesting convertEscapeSequences:');

    const testCases = [
        {
            input: 'Line 1\\nLine 2\\nLine 3',
            expected: 'Line 1\nLine 2\nLine 3',
            name: 'Basic newlines'
        },
        {
            input: 'Tab\\tCharacter',
            expected: 'Tab\tCharacter',
            name: 'Tab character'
        },
        {
            input: 'Quoted \\"string\\"',
            expected: 'Quoted "string"',
            name: 'Double quotes'
        }
    ];

    for (const test of testCases) {
        const result = convertEscapeSequences(test.input);
        const passed = result === test.expected;

        console.log(`- ${test.name}: ${passed ? 'PASSED' : 'FAILED'}`);
        if (!passed) {
            console.log(`  Expected: ${JSON.stringify(test.expected)}`);
            console.log(`  Got: ${JSON.stringify(result)}`);
        }
    }
}

// Test preprocessDiff function
function testPreprocessDiff() {
    console.log('\nTesting preprocessDiff:');

    const testCases = [
        {
            input: '@@ -1,3 +1,4 @@\n Line 1\n-Line 2\n+Line 2 modified\n+Line 2.5',
            expected: '@@ -1,3 +1,4 @@ \n Line 1\n-Line 2\n+Line 2 modified\n+Line 2.5',
            name: 'Add space after hunk header'
        },
        {
            input: '@@ -1,3 +1,4 @@ \n Line 1\nLine 2\n+Line 3',
            expected: '@@ -1,3 +1,4 @@ \n Line 1\n Line 2\n+Line 3',
            name: 'Add space prefix to line without prefix'
        }
    ];

    for (const test of testCases) {
        const result = preprocessDiff(test.input);
        const passed = result === test.expected;

        console.log(`- ${test.name}: ${passed ? 'PASSED' : 'FAILED'}`);
        if (!passed) {
            console.log(`  Expected: ${JSON.stringify(test.expected)}`);
            console.log(`  Got: ${JSON.stringify(result)}`);
        }
    }
}

// Test applyDiffToContent function
function testApplyDiffToContent() {
    console.log('\nTesting applyDiffToContent:');

    const testCases = [
        // Test case for the user's specific app.py and diff with incomplete hunk header
        {
            original: 'def main():\n    print("Hello, world!")\n\nif __name__ == "__main__":\n    main()',
            diff: '--- app.py\n+++ app.py\n@@\n+def sample_function():\n+    print("This is a sample function for testing diffToFile.")\n',
            expected: 'def main():\n    print("Hello, world!")\n\nif __name__ == "__main__":\n    main()',
            name: 'User app.py with incomplete hunk header',
            validate: (result) => {
                // This test is expected to fail because the hunk header is incomplete
                // The diff parser should return the original content unchanged
                if (result !== 'def main():\n    print("Hello, world!")\n\nif __name__ == "__main__":\n    main()') {
                    return 'Original content should be returned unchanged when diff has invalid hunk header';
                }
                return null; // No error
            }
        },
        // Test case for the user's specific app.py and diff with fixed hunk header
        {
            original: 'def main():\n    print("Hello, world!")\n\nif __name__ == "__main__":\n    main()',
            diff: '--- app.py\n+++ app.py\n@@ -2,0 +3,3 @@\n+def sample_function():\n+    print("This is a sample function for testing diffToFile.")\n+',
            expected: 'def main():\n    print("Hello, world!")\ndef sample_function():\n    print("This is a sample function for testing diffToFile.")\n\n\nif __name__ == "__main__":\n    main()',
            name: 'User app.py with fixed hunk header',
            validate: (result) => {
                // Check if the original content is preserved
                if (!result.includes('def main():')) {
                    return 'Original function "main" not preserved in result';
                }
                // Check if the new function is added
                if (!result.includes('def sample_function():')) {
                    return 'New function "sample_function" not found in result';
                }
                // Check if the function body is correct
                if (!result.includes('print("This is a sample function for testing diffToFile.")')) {
                    return 'Function body not correct';
                }
                // Check if the functions are in the correct order
                if (result.indexOf('def main():') > result.indexOf('def sample_function():')) {
                    return 'Functions in wrong order: sample_function should come after main';
                }
                return null; // No error
            }
        },
        {
            original: 'Line 1\nLine 2\nLine 3',
            diff: '@@ -1,3 +1,3 @@\n Line 1\n-Line 2\n+Line 2 modified\n Line 3',
            expected: 'Line 1\nLine 2 modified\nLine 3',
            name: 'Simple modification',
            validate: (result) => {
                // Check if the modified line is present
                if (!result.includes('Line 2 modified')) {
                    return 'Modified line "Line 2 modified" not found in result';
                }
                // Check if the original line is removed
                if (result.includes('Line 2\nLine 2 modified')) {
                    return 'Original line "Line 2" still present in result';
                }
                return null; // No error
            }
        },
        {
            original: 'Line 1\nLine 2\nLine 3',
            diff: '@@ -1,3 +1,4 @@\n Line 1\n Line 2\n+Line 2.5\n Line 3',
            expected: 'Line 1\nLine 2\nLine 2.5\nLine 3',
            name: 'Line addition',
            validate: (result) => {
                // Check if the added line is present
                if (!result.includes('Line 2.5')) {
                    return 'Added line "Line 2.5" not found in result';
                }
                // Check if the line is added in the correct position
                if (!result.includes('Line 2\nLine 2.5\nLine 3')) {
                    return 'Added line "Line 2.5" not in the correct position';
                }
                return null; // No error
            }
        },
        {
            original: 'Line 1\nLine 2\nLine 3',
            diff: '@@ -1,3 +1,2 @@\n Line 1\n-Line 2\n Line 3',
            expected: 'Line 1\nLine 3',
            name: 'Line deletion',
            validate: (result) => {
                // Check if the deleted line is removed
                if (result.includes('Line 2')) {
                    return 'Deleted line "Line 2" still present in result';
                }
                // Check if the remaining lines are in the correct order
                if (!result.includes('Line 1\nLine 3')) {
                    return 'Remaining lines not in the correct order';
                }
                return null; // No error
            }
        },
        {
            original: 'def fibonacci(n):\n    if n <= 1:\n        return n\n    return fibonacci(n-1) + fibonacci(n-2)',
            diff: '@@ -1,4 +1,6 @@\n def fibonacci(n):\n+    # Base case\n     if n <= 1:\n         return n\n+    # Recursive case\n     return fibonacci(n-1) + fibonacci(n-2)',
            expected: 'def fibonacci(n):\n    # Base case\n    if n <= 1:\n        return n\n    # Recursive case\n    return fibonacci(n-1) + fibonacci(n-2)',
            name: 'Comment addition',
            validate: (result) => {
                // Check if the comments are added
                if (!result.includes('# Base case')) {
                    return 'Comment "# Base case" not found in result';
                }
                if (!result.includes('# Recursive case')) {
                    return 'Comment "# Recursive case" not found in result';
                }
                // Check if the comments are in the correct positions
                if (!result.includes('# Base case\n    if n <= 1:')) {
                    return 'Comment "# Base case" not in the correct position';
                }
                if (!result.includes('# Recursive case\n    return fibonacci')) {
                    return 'Comment "# Recursive case" not in the correct position';
                }
                return null; // No error
            }
        },
        {
            original: 'def fibonacci(n):\n    if n <= 1:\n        return n\n    return fibonacci(n-1) + fibonacci(n-2)',
            diff: '--- a.py\n+++ b.py\n@@ -1,4 +1,7 @@\n def fibonacci(n):\n     if n <= 1:\n         return n\n     return fibonacci(n-1) + fibonacci(n-2)\n+\n+def fibonacci_sequence(n):\n+    return [fibonacci(i) for i in range(n)]',
            expected: 'def fibonacci(n):\n    if n <= 1:\n        return n\n    return fibonacci(n-1) + fibonacci(n-2)\n\ndef fibonacci_sequence(n):\n    return [fibonacci(i) for i in range(n)]',
            name: 'Function addition with file headers',
            validate: (result) => {
                // Check if the new function is added
                if (!result.includes('def fibonacci_sequence(n):')) {
                    return 'New function "fibonacci_sequence" not found in result';
                }
                // Check if the original function is preserved
                if (!result.includes('def fibonacci(n):')) {
                    return 'Original function "fibonacci" not preserved in result';
                }
                // Check if the functions are in the correct order
                if (!result.includes('def fibonacci(n):') || !result.includes('def fibonacci_sequence(n):')) {
                    return 'Functions not in the correct order';
                }
                if (result.indexOf('def fibonacci(n):') > result.indexOf('def fibonacci_sequence(n):')) {
                    return 'Functions in wrong order: fibonacci_sequence should come after fibonacci';
                }
                return null; // No error
            }
        },
        {
            original: '# --- FIBONACCI FUNCTION FOR DIFF TESTING ---\ndef fibonacci(n):\n    """Return the nth Fibonacci number."""\n    if n <= 0:\n        return 0\n    elif n == 1:\n        return 1\n    else:\n        return fibonacci(n-1) + fibonacci(n-2)',
            diff: '@@ -1,9 +1,0 @@\n-# --- FIBONACCI FUNCTION FOR DIFF TESTING ---\n-def fibonacci(n):\n-    """Return the nth Fibonacci number."""\n-    if n <= 0:\n-        return 0\n-    elif n == 1:\n-        return 1\n-    else:\n-        return fibonacci(n-1) + fibonacci(n-2)',
            expected: '',
            name: 'Block removal',
            validate: (result) => {
                // Check if the entire block is removed
                if (result.length > 0) {
                    return `Expected empty result, but got ${result.length} characters`;
                }
                // Check if specific content is removed
                if (result.includes('fibonacci')) {
                    return 'Function name "fibonacci" still present in result';
                }
                return null; // No error
            }
        },
        {
            original: '# --- FIBONACCI FUNCTION FOR DIFF TESTING ---\ndef fibonacci(n):\n    """Return the nth Fibonacci number."""\n    if n <= 0:\n        return 0\n    elif n == 1:\n        return 1\n    else:\n        return fibonacci(n-1) + fibonacci(n-2)',
            diff: '--- original\n+++ modified\n@@ -1,9 +1,0 @@\n-# --- FIBONACCI FUNCTION FOR DIFF TESTING ---\n-def fibonacci(n):\n-    """Return the nth Fibonacci number."""\n-    if n <= 0:\n-        return 0\n-    elif n == 1:\n-        return 1\n-    else:\n-        return fibonacci(n-1) + fibonacci(n-2)',
            expected: '',
            name: 'Block removal with file headers',
            validate: (result) => {
                // Check if the entire block is removed
                if (result.length > 0) {
                    return `Expected empty result, but got ${result.length} characters`;
                }
                // Check if specific content is removed
                if (result.includes('fibonacci')) {
                    return 'Function name "fibonacci" still present in result';
                }
                return null; // No error
            }
        },
        {
            original: '# TODO: Add main logic here\nimport os\nimport re\nimport pandas as pd\nfrom fastapi import FastAPI, Form, Request\nfrom fastapi.responses import HTMLResponse, StreamingResponse\nfrom fastapi.templating import Jinja2Templates\nfrom fastapi.staticfiles import StaticFiles\nfrom dotenv import load_dotenv, find_dotenv\nimport dspy\nimport io\nfrom PIL import Image, ImageDraw\n\n# --- ENSURE FOLDERS EXIST FIRST ---\nos.makedirs("templates", exist_ok=True)\nos.makedirs("static", exist_ok=True)\n\n# --- LOAD ENVIRONME…ubtypes": subtypes,\n        "default_prompt": prompt,\n        "results": mapping,\n        "selected_subtype": subtype,\n    })\n\n# --- IMAGE ROUTE ---\n@app.get("/image")\ndef get_image():\n    # Create a simple image with PIL\n    img = Image.new(\'RGB\', (200, 100), color=(73, 109, 137))\n    d = ImageDraw.Draw(img)\n    d.text((10, 40), "Hello, Image!", fill=(255, 255, 0))\n    buf = io.BytesIO()\n    img.save(buf, format=\'PNG\')\n    buf.seek(0)\n    return StreamingResponse(buf, media_type="image/png")\n',
            diff: '--- app.py\n+++ app.py\n@@ -22,0 +23,3 @@\n+def sample_function():\n+    print("This is a sample function for testing diffToFile.")\n+',
            expected: '# TODO: Add main logic here\nimport os\nimport re\nimport pandas as pd\nfrom fastapi import FastAPI, Form, Request\nfrom fastapi.responses import HTMLResponse, StreamingResponse\nfrom fastapi.templating import Jinja2Templates\nfrom fastapi.staticfiles import StaticFiles\nfrom dotenv import load_dotenv, find_dotenv\nimport dspy\nimport io\nfrom PIL import Image, ImageDraw\n\n# --- ENSURE FOLDERS EXIST FIRST ---\nos.makedirs("templates", exist_ok=True)\nos.makedirs("static", exist_ok=True)\n\n# --- LOAD ENVIRONME…ubtypes": subtypes,\n        "default_prompt": prompt,\n        "results": mapping,\n        "selected_subtype": subtype,\n    })\ndef sample_function():\n    print("This is a sample function for testing diffToFile.")\n\n\n# --- IMAGE ROUTE ---\n@app.get("/image")\ndef get_image():\n    # Create a simple image with PIL\n    img = Image.new(\'RGB\', (200, 100), color=(73, 109, 137))\n    d = ImageDraw.Draw(img)\n    d.text((10, 40), "Hello, Image!", fill=(255, 255, 0))\n    buf = io.BytesIO()\n    img.save(buf, format=\'PNG\')\n    buf.seek(0)\n    return StreamingResponse(buf, media_type="image/png")\n',
            name: 'Add function to FastAPI app',
            validate: (result) => {
                // Check if the new function is added
                if (!result.includes('def sample_function():')) {
                    return 'New function "sample_function" not found in result';
                }
                // Check if the function body is correct
                if (!result.includes('print("This is a sample function for testing diffToFile.")')) {
                    return 'Function body not correct';
                }
                // Check if the function is in the correct position (after the LOAD_ENVIRONME section)
                const loadEnvIndex = result.indexOf('# --- LOAD ENVIRONME');
                const sampleFuncIndex = result.indexOf('def sample_function():');
                const imageRouteIndex = result.indexOf('# --- IMAGE ROUTE ---');

                if (loadEnvIndex === -1 || sampleFuncIndex === -1 || imageRouteIndex === -1) {
                    return 'One or more expected sections not found';
                }

                if (!(loadEnvIndex < sampleFuncIndex && sampleFuncIndex < imageRouteIndex)) {
                    return 'Function not in the correct position';
                }

                return null; // No error
            }
        }
    ];

    for (const test of testCases) {
        const result = applyDiffToContent(test.original, test.diff);

        // Basic validation - check if the result matches the expected output
        const basicPassed = result === test.expected;

        // Advanced validation - check specific aspects of the result
        let validationError = null;
        if (test.validate) {
            validationError = test.validate(result);
        }

        const passed = basicPassed && !validationError;

        console.log(`- ${test.name}: ${passed ? 'PASSED' : 'FAILED'}`);
        if (!passed) {
            if (!basicPassed) {
                console.log(`  Expected: ${JSON.stringify(test.expected)}`);
                console.log(`  Got: ${JSON.stringify(result)}`);
            }

            if (validationError) {
                console.log(`  Validation error: ${validationError}`);
            }

            // Show diff for debugging
            console.log('  Original:');
            console.log(test.original.split('\n').map(line => `    ${line}`).join('\n'));
            console.log('  Diff:');
            console.log(test.diff.split('\n').map(line => `    ${line}`).join('\n'));
            console.log('  Result:');
            console.log(result.split('\n').map(line => `    ${line}`).join('\n'));
        }
    }
}

// Run the tests
runTests();
