import { JupyterFrontEnd } from '@jupyterlab/application';
import { app, functions } from './jupyter_integrations';
import { streamingState } from "./jupyter_integrations";
import { CodeMirrorEditor, jupyterTheme, jupyterHighlightStyle } from '@jupyterlab/codemirror';
import * as DiffMatchPatch from 'diff-match-patch';
import { Widget } from '@lumino/widgets';
import { Message } from '@lumino/messaging';

// Import necessary CodeMirror modules
import { StateEffect, StateField, EditorState, Text, Extension, Compartment } from '@codemirror/state';
import { Decoration, EditorView, ViewPlugin } from '@codemirror/view';
import { MergeView } from '@codemirror/merge';
import { LanguageSupport, syntaxHighlighting } from '@codemirror/language';

// Import language support modules
import { python } from '@codemirror/lang-python';
import { javascript } from '@codemirror/lang-javascript';
import { json } from '@codemirror/lang-json';
import { markdown } from '@codemirror/lang-markdown';
import { html } from '@codemirror/lang-html';
import { css } from '@codemirror/lang-css';

// Import diff utilities from the module
import { applyDiffToContent } from '../utils/diff-utils';

// Debug function to log information about the editor state
function debugEditorState(editor: EditorView, label: string) {
    console.log(`Debug ${label}:`, {
        hasFocus: editor.hasFocus,
        docLength: editor.state.doc.length
    });
}

// Function to get language extensions for a file based on its extension
function getLanguageExtensionsForFile(filePath: string): Extension[] {
    const fileExtension = filePath.split('.').pop()?.toLowerCase() || '';
    const extensions: Extension[] = [];

    // Always add JupyterLab's syntax highlighting
    extensions.push(syntaxHighlighting(jupyterHighlightStyle));

    // Add language support based on file extension
    let languageSupport: Extension | null = null;

    switch (fileExtension) {
        case 'py':
            languageSupport = python();
            break;
        case 'js':
            languageSupport = javascript();
            break;
        case 'ts':
            languageSupport = javascript({ typescript: true });
            break;
        case 'jsx':
            languageSupport = javascript({ jsx: true });
            break;
        case 'tsx':
            languageSupport = javascript({ jsx: true, typescript: true });
            break;
        case 'json':
            languageSupport = json();
            break;
        case 'md':
            languageSupport = markdown();
            break;
        case 'html':
        case 'htm':
            languageSupport = html();
            break;
        case 'css':
            languageSupport = css();
            break;
        // Add more language support as needed
    }

    if (languageSupport) {
        extensions.push(languageSupport);
        console.log(`Added language support for ${fileExtension}`);
    } else {
        console.log(`No specific language support for ${fileExtension}, using default highlighting`);
    }

    return extensions;
}

// Test function to verify diff application
function testDiffApplication() {
    // Test 1: Standard diff with proper hunk header
    const originalContent1 = 'Line 1\nLine 2\nLine 3';
    const diff1 = '@@ -1,3 +1,3 @@\n Line 1\n-Line 2\n+Line 2 modified\n Line 3';

    console.log('Test 1: Standard diff with proper hunk header');
    console.log('Original content:', originalContent1);
    console.log('Diff:', diff1);

    const patchedContent1 = applyDiffToContent(originalContent1, diff1, true);
    console.log('Patched content:', patchedContent1);

    const expected1 = 'Line 1\nLine 2 modified\nLine 3';
    console.log('Expected content:', expected1);
    console.log('Test 1 result:', patchedContent1 === expected1 ? 'PASSED' : 'FAILED');

    // Test 2: Diff with missing line numbers in hunk header
    const originalContent2 = 'def main():\n    print("Hello, world!")\n\nif __name__ == "__main__":\n    main()';
    const diff2 = '--- app.py\n+++ app.py\n@@\n+def sample_function():\n+    print("This is a sample function for testing diffToFile.")\n';

    console.log('\nTest 2: Diff with missing line numbers in hunk header');
    console.log('Original content:', originalContent2);
    console.log('Diff:', diff2);

    const patchedContent2 = applyDiffToContent(originalContent2, diff2, true);
    console.log('Patched content:', patchedContent2);

    // The expected result should have the new function added
    const expected2 = 'def main():\n    print("Hello, world!")\n\ndef sample_function():\n    print("This is a sample function for testing diffToFile.")\n\nif __name__ == "__main__":\n    main()';
    console.log('Expected content:', expected2);
    console.log('Test 2 result:', patchedContent2 === expected2 ? 'PASSED' : 'FAILED');

    // Test 3: Fix the diff by adding line numbers to the hunk header
    const diff3 = '--- app.py\n+++ app.py\n@@ -1,5 +3,2 @@\n+def sample_function():\n+    print("This is a sample function for testing diffToFile.")\n';

    console.log('\nTest 3: Fixed diff with proper hunk header');
    console.log('Original content:', originalContent2);
    console.log('Diff:', diff3);

    const patchedContent3 = applyDiffToContent(originalContent2, diff3, true);
    console.log('Patched content:', patchedContent3);
    console.log('Test 3 result:', patchedContent3 === expected2 ? 'PASSED' : 'FAILED');

    // Test 4: Fibonacci example with docstring addition
    const originalContent4 = 'def print_fibonacci(n):\n    a, b = 0, 1\n    for _ in range(n):\n        print(a)\n        a, b = b, a + b\n\n# Print the first 10 Fibonacci numbers\nprint_fibonacci(10)\n';
    const diff4 = '--- fibonacci.py\t2024-06-10 12:00:00.000000000 +0000\n+++ fibonacci.py\t2024-06-10 12:01:00.000000000 +0000\n@@ -1,6 +1,8 @@\n+"""This program prints the first n Fibonacci numbers"""\n+\ndef print_fibonacci(n):\n    a, b = 0, 1\n    for _ in range(n):\n        print(a)\n        a, b = b, a + b\n\n# Print the first 10 Fibonacci numbers\nprint_fibonacci(10)\n';

    console.log('\nTest 4: Fibonacci example with docstring addition');
    console.log('Original content:', originalContent4);
    console.log('Diff:', diff4);

    const patchedContent4 = applyDiffToContent(originalContent4, diff4, true);
    console.log('Patched content:', patchedContent4);

    const expected4 = '"""This program prints the first n Fibonacci numbers"""\n\ndef print_fibonacci(n):\n    a, b = 0, 1\n    for _ in range(n):\n        print(a)\n        a, b = b, a + b\n\n# Print the first 10 Fibonacci numbers\nprint_fibonacci(10)\n';
    console.log('Expected content:', expected4);
    console.log('Test 4 result:', patchedContent4 === expected4 ? 'PASSED' : 'FAILED');
}

// Run the test when the module is loaded
testDiffApplication();


function unescapeString(input: string): string {
    if (!input) return input;

    // First handle the standard escape sequences
    let result = input
        .replace(/\\n/g, '\n')       // newline
        .replace(/\\r/g, '\r')       // carriage return
        .replace(/\\t/g, '\t')       // tab
        .replace(/\\b/g, '\b')       // backspace
        .replace(/\\f/g, '\f')       // form feed
        .replace(/\\v/g, '\v')       // vertical tab
        .replace(/\\\\/g, '\\')      // backslash
        .replace(/\\"/g, '"')        // double quote
        .replace(/\\'/g, "'");       // single quote

    // Handle hex escapes (\xXX)
    result = result.replace(/\\x([0-9A-Fa-f]{2})/g, (_, hex) =>
        String.fromCharCode(parseInt(hex, 16))
    );

    // Handle unicode escapes (\uXXXX)
    result = result.replace(/\\u([0-9A-Fa-f]{4})/g, (_, hex) =>
        String.fromCharCode(parseInt(hex, 16))
    );

    // Handle unicode code point escapes (\u{XXXXX})
    result = result.replace(/\\u\{([0-9A-Fa-f]+)\}/g, (_, hex) =>
        String.fromCodePoint(parseInt(hex, 16))
    );

    // Handle null character escape (\0)
    result = result.replace(/\\0/g, '\0');

    // Normalize line endings (convert \r\n to \n)
    result = result.replace(/\r\n/g, '\n');

    return result;
}





function fixPartialDiff(diff: string): string {
    const lines = diff.split('\n');
    const cleanedLines: string[] = [];
    let insideHunk = false;

    for (const line of lines) {
        // Skip empty lines
        if (line.trim() === '') {
            continue;
        }

        // Pass through file headers and hunk headers unchanged
        if (line.startsWith('---') || line.startsWith('+++') || line.startsWith('@@')) {
            cleanedLines.push(line);
            if (line.startsWith('@@')) {
                insideHunk = true;
            }
            continue;
        }

        // Inside a hunk, only keep lines with proper prefixes
        if (insideHunk) {
            if (line.startsWith('+') || line.startsWith('-') || line.startsWith(' ')) {
                cleanedLines.push(line);
            }
            // Skip lines without proper prefixes
        } else {
            // Not inside a hunk, just add the line
            cleanedLines.push(line);
        }
    }

    return cleanedLines.join('\n');
}



var mergeViews = {};
var mergeWidgets = {}

export function init_diff() {
    functions["diffToFile"] = {
        "def": {
            "name": "diffToFile",
            "description": "Apply unified diff to a file. Unified diff format only!",
            "arguments": {
                "filePath": {
                    "type": "string",
                    "name": "Relative path to the file to display in merge view. Relative! "
                },
                "diff": {
                    "type": "string",
                    "name": "Unified diff content to apply to the file (must be in unified diff format)"
                }
            }
        },
        "func": async (args: any, streaming: boolean = false, call_id: string = undefined): Promise<string> => {
            // Function to apply syntax highlighting directly to the editors
            function updateDocB(mergeView: MergeView, newContent: string): boolean {
                try {
                    // Try to access the editor for doc B directly through the mergeView object
                    if (!mergeView.b || !mergeView.b.state) {
                        console.error('Could not access state for doc B');
                        return false;
                    }

                    // Get the current state and create a new state with the updated content
                    const currentState = mergeView.b.state;

                    // Create a transaction to replace the entire document content
                    mergeView.b.dispatch({
                        changes: {
                            from: 0,
                            to: currentState.doc.length,
                            insert: newContent
                        }
                    });

                    console.log('Successfully updated doc B');
                    return true;
                } catch (err) {
                    console.error('Error updating doc B:', err);
                    return false;
                }
            }




            const applySyntaxHighlighting = (mergeView) => {
                try {
                    const editors = mergeView.dom.querySelectorAll('.cm-editor');
                    console.log(`Found ${editors.length} editors in merge view`);

                    editors.forEach((editorElement, index) => {
                        const editorView = (editorElement as any).view;
                        if (editorView) {
                            debugEditorState(editorView, `Editor ${index}`);

                            // Add a class to the editor element based on file extension
                            const fileExtension = filePath.split('.').pop()?.toLowerCase() || '';
                            editorElement.classList.add(`language-${fileExtension}`);

                            // Force a refresh of the editor view
                            setTimeout(() => {
                                try {
                                    // Dispatch a dummy transaction to force a refresh
                                    editorView.dispatch({});
                                } catch (err) {
                                    console.error(`Error refreshing editor ${index}:`, err);
                                }
                            }, 100);
                        } else {
                            console.log(`Could not access view for editor ${index}`);
                        }
                    });
                } catch (err) {
                    console.error("Error applying syntax highlighting:", err);
                }
            };



            if (!app) {
                return JSON.stringify({ error: "JupyterLab app not initialized" });
            }

            const { contents } = app.serviceManager;
            const { filePath, diff } = args;

            try {
                // Read the file content
                let fileContent;
                try {
                    fileContent = await contents.get(filePath);
                } catch (err) {
                    return JSON.stringify({
                        "status": "fail",
                        "message": `Cannot open file: ${filePath} does not exist`
                    });
                }

                const originalContent = fileContent.content as string;

                console.log('DEBUG - Original content length:', originalContent.length);
                console.log('DEBUG - Diff provided:', !!diff);
                if (diff) {
                    console.log('DEBUG - Diff length:', diff.length);
                }

                // Apply the diff to get the patched content
                // We'll use false for silent to see debug logs
                const unescapedDiff = unescapeString(diff);
                const fixedDiff = fixPartialDiff(unescapedDiff);


                console.log('DEBUG - After fixPartialDiff:');
                console.log(fixedDiff);
                console.log('DEBUG - Fixed diff length:', fixedDiff.length);

                // Check if the fixed diff is different from the original
                console.log('DEBUG - Diff changed by fixPartialDiff:', diff !== fixedDiff);

                // Apply both versions of the diff for comparison
                const patchedContent = diff ? applyDiffToContent(originalContent, fixedDiff, false) : originalContent;
                const patchedContent0 = diff ? applyDiffToContent(originalContent, unescapedDiff, false) : originalContent;

                const originalLength = originalContent.length;
                const patchedLength = patchedContent.length;
                const patchedLength0 = patchedContent0.length;

                if ((originalLength != patchedLength) || (originalLength != patchedLength0)) {
                    //alert(`${originalLength} ${patchedLength} ${patchedLength0}`)
                }

                console.log('DEBUG - Original content length:', originalLength);
                console.log('DEBUG - Patched content length (fixed diff):', patchedLength);
                console.log('DEBUG - Patched content length (original diff):', patchedLength0);
                console.log('DEBUG - Content changed (fixed diff):', patchedContent !== originalContent);
                console.log('DEBUG - Content changed (original diff):', patchedContent0 !== originalContent);
                console.log('DEBUG - Fixed diff and original diff produce same result:', patchedContent === patchedContent0);


                if (mergeViews[call_id] != undefined) {
                    updateDocB(mergeViews[call_id], patchedContent);
                } else if (mergeViews[call_id] == undefined) {

                    // Create a container for the merge view
                    const container = document.createElement('div');
                    container.style.height = '100%';
                    container.style.overflow = 'auto';

                    // Get language extensions for the file and add JupyterLab theme
                    const languageExtensions = [jupyterTheme, ...getLanguageExtensionsForFile(filePath)];

                    // Add a style element for syntax highlighting using JupyterLab's CSS variables
                    const styleElement = document.createElement('style');
                    styleElement.textContent = `
                        /* Basic syntax highlighting styles using JupyterLab variables */
                        .cm-keyword { color: var(--jp-mirror-editor-keyword-color); font-weight: bold; }
                        .cm-comment { color: var(--jp-mirror-editor-comment-color); }
                        .cm-string { color: var(--jp-mirror-editor-string-color); }
                        .cm-number { color: var(--jp-mirror-editor-number-color); }
                        .cm-operator { color: var(--jp-mirror-editor-operator-color); }
                        .cm-property { color: var(--jp-mirror-editor-property-color); }
                        .cm-variable { color: var(--jp-mirror-editor-variable-color); }
                        .cm-function, .cm-def { color: var(--jp-mirror-editor-def-color); }
                        .cm-atom { color: var(--jp-mirror-editor-atom-color); }
                        .cm-meta { color: var(--jp-mirror-editor-meta-color); }
                        .cm-tag { color: var(--jp-mirror-editor-tag-color); }
                        .cm-attribute { color: var(--jp-mirror-editor-attribute-color); }
                        .cm-qualifier { color: var(--jp-mirror-editor-qualifier-color); }
                        .cm-bracket { color: var(--jp-mirror-editor-bracket-color); }
                        .cm-builtin { color: var(--jp-mirror-editor-builtin-color); }
                        .cm-special { color: var(--jp-mirror-editor-string-2-color); }
                    `;
                    document.head.appendChild(styleElement);

                    const mergeView = new MergeView({
                        a: {
                            doc: originalContent,
                            extensions: languageExtensions
                        },
                        b: {
                            doc: patchedContent,
                            extensions: languageExtensions
                        },
                        highlightChanges: true
                    });


                    mergeViews[call_id] = mergeView;

                    container.appendChild(mergeView.dom);

                    setTimeout(function () {
                        applySyntaxHighlighting(mergeView);
                    }, 500);

                    // Create a widget to hold the container
                    const widget = new Widget();
                    mergeWidgets[call_id] = widget;

                    widget.id = call_id;
                    widget.title.label = `Merge View: ${filePath}`;
                    widget.title.closable = true;
                    widget.node.appendChild(container);

                    // Add the widget to the main area and activate it
                    app.shell.add(widget, 'main');
                    app.shell.activateById(widget.id);

                }

                if (!streaming) {
                    await contents.save(filePath, {
                        type: 'file',
                        format: 'text',
                        content: patchedContent
                    });

                    // Close the merge view widget if it exists
                    if (mergeViews[call_id]) {
                        // Find the widget by ID and close it
                        const widget = mergeWidgets[call_id];
                        //const widget = app.shell.widgets('main').find(w => w.id === call_id);
                        if (widget) {
                            // Close the widget
                            widget.dispose();

                            // Force a UI refresh by using setTimeout
                            setTimeout(() => {
                                // Clean up our references
                                delete mergeViews[call_id];
                                delete mergeWidgets[call_id];

                                // Force a refresh of the application shell
                                //app.shell.update();

                                // Open the file in a normal editor
                                app.commands.execute('docmanager:close', { path: filePath });
                                app.commands.execute('docmanager:open', { path: filePath });
                            }, 100);
                        }
                    }

                    /*
                    // Open the file in a normal editor
                    try {
                        await app.commands.execute('docmanager:open', { path: filePath });
                    } catch (openErr) {
                        console.error('Error opening file after saving:', openErr);
                    }
                        */
                }

                return JSON.stringify({
                    "status": "ok",
                    "message": "Merge view opened successfully"
                });
            } catch (err) {
                return JSON.stringify({
                    "status": "fail",
                    "message": `Failed to open merge view: ${err.message}`
                });
            }
        }
    }
}
