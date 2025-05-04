import { JupyterFrontEnd } from '@jupyterlab/application';
import { app, functions } from './jupyter_integrations';
import { streamingState } from "./jupyter_integrations";
import { CodeMirrorEditor } from '@jupyterlab/codemirror';
import * as DiffMatchPatch from 'diff-match-patch';

// Import necessary CodeMirror modules
import { StateEffect, StateField } from '@codemirror/state';
import { Decoration, EditorView } from '@codemirror/view';

// CSS styles for diff highlighting
const diffStyles = `
/* Light mode styles */
.diff-added {
  background-color: rgba(0, 255, 0, 0.2);
  border-bottom: 1px solid #2cbe4e;
  text-decoration: none;
}

.diff-removed {
  background-color: rgba(255, 0, 0, 0.2);
  border-bottom: 1px solid #d73a49;
  text-decoration: line-through;
}

/* Dark mode styles */
@media (prefers-color-scheme: dark) {
  .diff-added {
    background-color: rgba(0, 255, 0, 0.3);
    border-bottom: 1px solid #4eca6a;
  }

  .diff-removed {
    background-color: rgba(255, 0, 0, 0.3);
    border-bottom: 1px solid #ff5370;
  }
}

/* JupyterLab-specific dark theme detection */
.jp-mod-presentationMode .diff-added,
.jp-mod-presentationMode .diff-removed,
.jp-mod-dark .diff-added,
.jp-mod-dark .diff-removed {
  filter: brightness(1.2) contrast(1.2);
}
`;

// Create decorations for added and removed text
const addedMark = Decoration.mark({ class: 'diff-added' });
const removedMark = Decoration.mark({ class: 'diff-removed' });

// Define a state effect for updating decorations
const highlightEffect = StateEffect.define<any>();

// Create a state field to manage decorations
const highlightField = StateField.define({
    create() {
        return Decoration.none;
    },
    update(decorations, tr) {
        // Check for our effect
        for (let e of tr.effects) {
            if (e.is(highlightEffect)) {
                return e.value;
            }
        }
        // Map decorations through changes
        return decorations.map(tr.changes);
    },
    provide: field => EditorView.decorations.from(field)
});

// Function to apply highlights based on diffs
function highlightDiffs(editor: any, diffs: Array<[number, string]>) {
    console.log('Highlighting diffs with editor:', editor);

    // Add styles to the document if they don't exist yet
    if (!document.getElementById('diff-styles')) {
        const styleElement = document.createElement('style');
        styleElement.id = 'diff-styles';
        styleElement.textContent = diffStyles;
        document.head.appendChild(styleElement);
        console.log('Added diff styles to document head');
    }

    // Get the CodeMirror EditorView instance
    const view = editor.editor;
    if (!view) {
        console.error('Could not get CodeMirror EditorView');
        return;
    }

    try {
        // Make sure the highlight field is registered
        view.dispatch({
            effects: StateEffect.appendConfig.of([highlightField])
        });

        // Get the current document text
        const doc = view.state.doc;
        console.log('Document length:', doc.length);

        // Process diffs to create better visual representation
        let additions = [];
        let currentPos = 0;

        // First, collect all additions
        for (const [op, text] of diffs) {
            if (text.length === 0) continue;

            try {
                if (op === 1) { // Insertion
                    // For insertions, use the current position directly
                    const from = currentPos;
                    const to = currentPos + text.length;

                    // Ensure positions are within document bounds
                    if (from >= 0 && to <= doc.length) {
                        additions.push({ from, to, text });
                        console.log(`Added decoration: ${from}-${to} for text "${text}"`);
                    } else {
                        console.warn(`Position out of bounds: ${from}-${to}, doc length: ${doc.length}`);
                    }
                }
            } catch (err) {
                console.error('Error processing diff:', err);
            }

            // Update position for next iteration
            if (op !== -1) { // Skip deletions when updating position
                currentPos += text.length;
            }
        }

        console.log('Collected additions:', additions.length);

        // Apply green highlighting to additions
        if (additions.length > 0) {
            // Create decoration ranges for additions
            const additionRanges = additions.map(a => addedMark.range(a.from, a.to));

            // Apply decorations
            view.dispatch({
                effects: highlightEffect.of(Decoration.set(additionRanges))
            });

            console.log('Applied green highlighting to additions');
        } else {
            console.log('No additions to highlight');
        }

        console.log('Applied decorations to editor with green highlighting for new content');
    } catch (err) {
        console.error('Error applying decorations:', err);
    }
}

export async function ensurePathExists(
    app: JupyterFrontEnd,
    fullPath: string
): Promise<void> {
    const contents = app.serviceManager.contents;
    const parts = fullPath.split('/');
    parts.pop(); // remove file name

    let currentPath = '';
    for (const part of parts) {
        currentPath = currentPath ? `${currentPath}/${part}` : part;

        try {
            const stat = await contents.get(currentPath);
            if (stat.type !== 'directory') {
                throw new Error(`${currentPath} exists but is not a directory`);
            }
        } catch (err: any) {
            if (err?.response?.status === 404 || /not found/i.test(err.message)) {
                // Create the directory using contents.save()
                await contents.save(currentPath, {
                    type: 'directory',
                    format: 'json',
                    content: null
                });
            } else {
                throw new Error(`Failed checking/creating directory ${currentPath}: ${err.message}`);
            }
        }
    }
}

// Helper function to validate if content is a valid diff
function isValidDiff(diffContent: string): boolean {
    // Check for common diff format patterns
    // Look for unified diff format headers like @@ -line,count +line,count @@
    const unifiedDiffPattern = /^@@\s+-\d+,?\d*\s+\+\d+,?\d*\s+@@/m;

    // Check for simplified diff format with just @@
    const simplifiedDiffPattern = /^@@$/m;

    // Check for diff headers like --- a/file or +++ b/file
    const diffHeaderPattern = /^(---|\+\+\+)\s+\S+/m;

    // Check for lines starting with +, -, or space
    const diffLinePattern = /^[\+\- ]/m;

    // A valid diff should have at least one of these patterns
    return unifiedDiffPattern.test(diffContent) ||
        simplifiedDiffPattern.test(diffContent) ||
        (diffHeaderPattern.test(diffContent) && diffLinePattern.test(diffContent));
}

export function init_fs() {
    functions["listFiles"] = {
        "def": {
            "name": "listFiles",
            "description": "List files and directories at a specified relative path. Ignore rootPath if it exists",
            "arguments": {
                "path": {
                    "type": "string",
                    "name": "Relative path to list files from. Relative!",
                    "default": "/"
                }
            }
        },
        "func": async (args: any): Promise<string> => {
            if (!app) {
                return JSON.stringify({ error: "JupyterLab app not initialized" });
            }

            const path = args.path || '/';
            const contents = app.serviceManager.contents;

            try {
                const listing = await contents.get(path, { content: true });

                if (listing.type !== 'directory') {
                    return JSON.stringify({
                        error: `Path '${path}' is not a directory`
                    });
                }

                const files = listing.content.map(item => ({
                    name: item.name,
                    path: item.path,
                    type: item.type,
                    last_modified: item.last_modified
                }));

                return JSON.stringify({
                    success: true,
                    files: files
                });
            } catch (error) {
                return JSON.stringify({
                    error: `Error listing files: ${error.message}`
                });
            }
        }
    }



    functions["writeToFile"] = {
        "def": {
            "name": "writeToFile",
            "description": "Opens a non-notebook file for editing (code, text, etc) and write into it",
            "arguments": {
                "filePath": {
                    "type": "string",
                    "name": "Relative path to the file to open. Relative! "
                },
                "content": {
                    "type": "string",
                    "name": "New content for the file. Entire file is being replaced by this!"
                }
            }
        },
        "func": async (args: any, streaming: boolean = false, call_id: string = undefined): Promise<string> => {
            if (!app) {
                return JSON.stringify({ error: "JupyterLab app not initialized" });
            }
            const { contents } = app.serviceManager;
            const { filePath, content } = args;

            if (call_id == undefined) return "dummy ok";

            // create the file if necessary
            await ensurePathExists(app, filePath);

            await contents.save(filePath, {
                type: 'file',
                format: 'text',
                content: content
            });

            let widget;

            try {
                widget = await app.commands.execute('docmanager:open', {
                    path: filePath,
                    factory: 'Editor'
                });
            } catch (err) {
                return JSON.stringify({
                    "status": "fail", "message": "could not open file",
                    "detail": `${err.message}`
                });
            }

            try {
                await Promise.race([
                    widget.context.ready,
                    new Promise((_, reject) => setTimeout(() => reject(new Error('Timeout waiting for context.ready')), 500))
                ]);
            } catch (err) {
                return JSON.stringify({ "status": "fail", "message": "could not open file" });
            }

            await widget.context.revert();

            //widget.content.model.sharedModel.setSource( content );
            //await widget.context.save();

            // Return current live content in the editor (unsaved edits included)
            return JSON.stringify({
                "status": "ok"
            })
        }
    }


    // Simplified function to apply a diff directly to text
    function applyDiffDirectly(diffContent: string, originalContent: string): string {
        // Normalize line endings and split into lines
        const normalizedDiff = diffContent.replace(/\\n/g, '\n').replace(/\r\n/g, '\n');
        const diffLines = normalizedDiff.split('\n');
        const originalLines = originalContent.split('\n');

        // Skip file headers
        let i = 0;
        while (i < diffLines.length && (diffLines[i].startsWith('---') || diffLines[i].startsWith('+++'))) {
            i++;
        }

        // Skip hunk header
        if (i < diffLines.length && diffLines[i].startsWith('@@')) {
            i++;
        }

        // Process the diff lines
        let result = [...originalLines];
        let contextFound = false;
        let insertPosition = -1;

        // First, find the context
        for (let j = i; j < diffLines.length; j++) {
            const line = diffLines[j];

            if (line.startsWith(' ')) {
                // This is a context line, find it in the original content
                const contextLine = line.substring(1);
                for (let k = 0; k < originalLines.length; k++) {
                    if (originalLines[k] === contextLine) {
                        insertPosition = k;
                        contextFound = true;
                        break;
                    }
                }
                if (contextFound) break;
            }
        }

        // If no context found, try to find the first line that starts with '-'
        if (!contextFound) {
            for (let j = i; j < diffLines.length; j++) {
                const line = diffLines[j];

                if (line.startsWith('-')) {
                    // This is a deletion line, find it in the original content
                    const deletionLine = line.substring(1);
                    for (let k = 0; k < originalLines.length; k++) {
                        if (originalLines[k] === deletionLine) {
                            insertPosition = k;
                            contextFound = true;
                            break;
                        }
                    }
                    if (contextFound) break;
                }
            }
        }

        // If still no context found, default to the beginning
        if (!contextFound) {
            insertPosition = 0;
        }

        // Now apply the changes
        let currentPosition = insertPosition;

        for (let j = i; j < diffLines.length; j++) {
            const line = diffLines[j];

            if (line.startsWith('+')) {
                // Addition
                result.splice(currentPosition + 1, 0, line.substring(1));
                currentPosition++;
            } else if (line.startsWith('-')) {
                // Deletion
                if (currentPosition < result.length && result[currentPosition] === line.substring(1)) {
                    result.splice(currentPosition, 1);
                }
            } else if (line.startsWith(' ')) {
                // Context line, move to next
                currentPosition++;
            }
        }

        return result.join('\n');
    }

    functions["diffToFile"] = {
        "def": {
            "name": "diffToFile",
            "description": "Applies a diff to a file and displays the changes visually with syntax highlighting.",
            "arguments": {
                "filePath": {
                    "type": "string",
                    "name": "Relative path to the file to apply the diff to. Relative!"
                },
                "diff": {
                    "type": "string",
                    "name": "Diff content to apply to the file (unified diff format)"
                },
                "visualize": {
                    "type": "boolean",
                    "name": "Whether to visualize the changes with highlighting",
                    "default": true
                }
            }
        },
        "func": async (args: any, streaming: boolean = false, call_id: string = undefined): Promise<string> => {
            if (!app) {
                return JSON.stringify({ error: "JupyterLab app not initialized" });
            }

            const { contents } = app.serviceManager;
            const { filePath, diff, visualize = true } = args;

            try {
                // Get the current content of the file
                let fileContent;
                try {
                    fileContent = await contents.get(filePath);
                } catch (err) {
                    return JSON.stringify({
                        "status": "fail",
                        "message": `Cannot apply diff: file ${filePath} does not exist`
                    });
                }

                const originalContent = fileContent.content as string;

                // Apply the diff directly to the original content
                const newContent = applyDiffDirectly(diff, originalContent);

                // Open the file in the editor
                let widget;
                try {
                    widget = await app.commands.execute('docmanager:open', {
                        path: filePath,
                        factory: 'Editor'
                    });
                } catch (err) {
                    return JSON.stringify({
                        "status": "fail",
                        "message": "could not open file",
                        "detail": `${err.message}`
                    });
                }

                // Wait for the widget to be ready
                try {
                    await Promise.race([
                        widget.context.ready,
                        new Promise((_, reject) => setTimeout(() => reject(new Error('Timeout waiting for context.ready')), 500))
                    ]);
                } catch (err) {
                    return JSON.stringify({ "status": "fail", "message": "could not open file" });
                }

                // Get the CodeMirror editor instance
                const editor = widget.content.editor;
                const codeMirrorInstance = editor.editor; // This is the CodeMirror EditorView

                if (!codeMirrorInstance) {
                    return JSON.stringify({
                        "status": "fail",
                        "message": "Could not access CodeMirror editor instance. Please contact the developer."
                    });
                }

                // Update the editor content with the new content from the diff
                widget.content.model.sharedModel.setSource(newContent);

                // Then, save the file through the widget context to ensure synchronization
                try {
                    await widget.context.save();
                } catch (err) {
                    console.error('Error saving file:', err);
                    return JSON.stringify({
                        "status": "fail",
                        "message": `Failed to save file: ${err.message}`
                    });
                }

                // Apply visual highlighting to show the changes
                if (visualize && editor) {
                    // Initialize the diff-match-patch instance for highlighting
                    const dmp = new DiffMatchPatch.diff_match_patch();

                    // We need to wait a bit for the editor to update
                    // Try multiple times with increasing delays to ensure highlighting works
                    const attemptHighlighting = (attempt = 1) => {
                        console.log(`Highlighting attempt ${attempt}`);
                        try {
                            // Compute diffs between original and current content for highlighting
                            const currentText = widget.content.model.sharedModel.getSource();
                            const computedDiffs = dmp.diff_main(originalContent, currentText);
                            dmp.diff_cleanupSemantic(computedDiffs);

                            // Apply highlighting
                            highlightDiffs(editor, computedDiffs);

                            // If this is not the last attempt, schedule another try
                            if (attempt < 3) {
                                setTimeout(() => attemptHighlighting(attempt + 1), 500 * attempt);
                            }
                        } catch (err) {
                            console.error(`Error in highlighting attempt ${attempt}:`, err);
                            // Try again if not the last attempt
                            if (attempt < 3) {
                                setTimeout(() => attemptHighlighting(attempt + 1), 500 * attempt);
                            }
                        }
                    };

                    // Start the first attempt after a short delay
                    setTimeout(() => attemptHighlighting(), 200);
                }

                // Return the final content after applying the diff
                return JSON.stringify({
                    "status": "ok",
                    "message": "Diff applied successfully with visual highlighting",
                    "content": newContent
                });
            } catch (err) {
                return JSON.stringify({
                    "status": "fail",
                    "message": `Failed to apply diff: ${err.message}`
                });
            }
        }
    };


    functions["openFile"] = {
        "def": {
            "name": "openFile",
            "description": "Opens a non-notebook file for editing (code, text, etc) and returns its contents",
            "arguments": {
                "filePath": {
                    "type": "string",
                    "name": "Relative path to the file to open. Relative! "
                }
            }
        },
        "func": async (args: any): Promise<string> => {
            if (!app) {
                return JSON.stringify({ error: "JupyterLab app not initialized" });
            }
            const filePath = args["filePath"]

            const { contents } = app.serviceManager;
            let fileContent;

            // Ensure file exists (create if it doesn't)
            await ensurePathExists(app, filePath);
            try {
                try {
                    fileContent = await contents.get(filePath);
                } catch {
                    await contents.save(filePath, {
                        type: 'file',
                        format: 'text',
                        content: ''
                    });
                    fileContent = await contents.get(filePath);
                }
            } catch (err) {
                return JSON.stringify({
                    "status": "fail", "message": "could not open file",
                    "detail": `${err.message}`
                });
            }

            let widget;
            try {
                widget = await app.commands.execute('docmanager:open', {
                    path: filePath,
                    factory: 'Editor'
                });
            } catch (err) {
                return JSON.stringify({
                    "status": "fail", "message": "could not open file",
                    "detail": `${err.message}`
                });
            }

            try {
                await Promise.race([
                    widget.context.ready,
                    new Promise((_, reject) => setTimeout(() => reject(new Error('Timeout waiting for context.ready')), 500))
                ]);
            } catch (err) {
                return JSON.stringify({ "status": "fail", "message": "could not open file" });
            }

            const result = JSON.stringify({
                "status": "ok",
                "content": fileContent.content
            });

            return (result);
        }
    }

}
