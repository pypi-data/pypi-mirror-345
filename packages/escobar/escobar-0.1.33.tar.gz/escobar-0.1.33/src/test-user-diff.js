// Import the diff utilities
const { applyDiffToContent } = require('../lib/utils/diff-utils');

// Test the user's specific diff
function testUserDiff() {
    console.log('Testing user diff with incomplete hunk header...');

    // Original content
    const originalContent = 'def main():\n    print("Hello, world!")\n\nif __name__ == "__main__":\n    main()';

    // The user's diff with incomplete hunk header
    const userDiff = '--- app.py\n+++ app.py\n@@\n+def sample_function():\n+    print("This is a sample function for testing diffToFile.")\n';

    // Apply the diff
    console.log('Original content:');
    console.log(originalContent);
    console.log('\nDiff:');
    console.log(userDiff);

    const patchedContent = applyDiffToContent(originalContent, userDiff);

    console.log('\nPatched content:');
    console.log(patchedContent);

    // Expected result (with the function added)
    const expectedContent = 'def main():\n    print("Hello, world!")\n\ndef sample_function():\n    print("This is a sample function for testing diffToFile.")\nif __name__ == "__main__":\n    main()';

    console.log('\nExpected content:');
    console.log(expectedContent);

    // Check if the patched content matches the expected content
    const passed = patchedContent === expectedContent;
    console.log('\nTest result:', passed ? 'PASSED' : 'FAILED');

    if (!passed) {
        console.log('\nDifferences:');
        console.log('Expected length:', expectedContent.length);
        console.log('Actual length:', patchedContent.length);

        // Find the first difference
        for (let i = 0; i < Math.min(expectedContent.length, patchedContent.length); i++) {
            if (expectedContent[i] !== patchedContent[i]) {
                console.log(`First difference at position ${i}:`);
                console.log(`Expected: "${expectedContent.substring(i, i + 20)}..."`);
                console.log(`Actual: "${patchedContent.substring(i, i + 20)}..."`);
                break;
            }
        }
    }
}

// Run the test
testUserDiff();
