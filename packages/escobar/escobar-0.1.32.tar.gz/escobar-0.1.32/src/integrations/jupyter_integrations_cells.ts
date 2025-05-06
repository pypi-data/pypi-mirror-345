import { JupyterFrontEnd } from '@jupyterlab/application';
import { app, notebookTracker, functions } from './jupyter_integrations'
import { getActiveNotebook, validateCellIndex } from "./jupyter_integrations"
import { Cell, CellModel, ICellModel, CodeCell, MarkdownCell } from '@jupyterlab/cells';
import { ensurePathExists } from './jupyter_integrations_fs';

import { Notebook, NotebookPanel, NotebookModel, NotebookActions } from '@jupyterlab/notebook';

import { streamingState } from "./jupyter_integrations"

import {
    JupyterFrontEndPlugin
} from '@jupyterlab/application';



function insert_cell(tracked_notebook: Notebook, cellType: string, index: number) {
    var newCellIndex = index;
    if (index <= 0) {
        tracked_notebook.activeCellIndex = 0;
        NotebookActions.insertAbove(tracked_notebook);
        newCellIndex = 0;
        tracked_notebook.activeCellIndex = newCellIndex;
        NotebookActions.changeCellType(tracked_notebook, cellType);
    } else {
        tracked_notebook.activeCellIndex = index - 1;
        NotebookActions.insertBelow(tracked_notebook);
        newCellIndex = index;
        tracked_notebook.activeCellIndex = newCellIndex;
        NotebookActions.changeCellType(tracked_notebook, cellType);
    }
    return newCellIndex;
}


export function init_cells() {
    functions["insertExecuteCell"] = {
        "def": {
            "name": "insertExecuteCell",
            "description": "Index at which to place the new cell",
            "arguments": {
                "index": {
                    "type": "integer",
                    "name": "New cel lindex"
                },
                "cellType": {
                    "type": "string",
                    "name": "Type of the cell being edited (code/markdown)"
                },
                "content": {
                    "type": "string",
                    "name": "New content for the cell"
                }
            }
        },
        "func": async (args: any, streaming: boolean = false, call_id: string = undefined): Promise<string> => {
            var { index, cellType, content } = args;
            const current = notebookTracker.currentWidget

            app.shell.activateById(current.id)

            const tracked_notebook = current.content;
            index = typeof index === "string" ? parseInt(index, 10) : index;

            console.log(streaming, call_id, args, index)

            var newCellIndex = index <= 0 ? 0 : index;

            if (call_id != undefined) {
                if (streamingState[call_id] == undefined) {
                    streamingState[call_id] = index;
                    insert_cell(tracked_notebook, cellType, index);
                } else {
                    tracked_notebook.activeCellIndex = newCellIndex;
                }

                if (tracked_notebook.mode != "edit") {
                    tracked_notebook.activate();
                    tracked_notebook.mode = 'edit';
                }
                const activeCell = tracked_notebook.activeCell;
                activeCell.model.sharedModel.setSource(args["content"]);
                if (activeCell instanceof MarkdownCell) {
                    activeCell.rendered = true;
                }
            } else {
                tracked_notebook.activeCellIndex = newCellIndex;
                const activeCell = tracked_notebook.activeCell;
                activeCell.model.sharedModel.setSource(args["content"]);
                if (tracked_notebook.mode != "edit") {
                    tracked_notebook.activate();
                    tracked_notebook.mode = 'edit';
                }

                tracked_notebook.mode = "command"

                if (activeCell instanceof MarkdownCell) {
                    activeCell.rendered = true;
                    await current.context.save();
                    return "ok"
                } else {
                    const ststus = await NotebookActions.run(tracked_notebook, current.sessionContext)
                    const executionOutput = await functions["getCellOutput"].func({
                        index: index
                    })
                    await current.context.save();
                    return executionOutput
                }

            }

            return "ok"
        }
    }

    functions["editExecuteCell"] = {
        "def": {
            "name": "editExecuteCell",
            "description": "Edit the content of a cell by index and execute (render) it",
            "arguments": {
                "index": {
                    "type": "integer",
                    "name": "Index of the cell to edit"
                },
                "cellType": {
                    "type": "string",
                    "name": "Type of the cell being edited"
                },
                "content": {
                    "type": "string",
                    "name": "New content for the cell"
                }
            }
        },
        "func": async (args: any, streaming: boolean = false, call_id: string = undefined): Promise<string> => {
            if (!app) {
                return JSON.stringify({ error: "JupyterLab app not initialized" });
            }

            var { index, cellType, content } = args;
            index = typeof index === "string" ? parseInt(index, 10) : index;

            try {
                const current = notebookTracker.currentWidget

                app.shell.activateById(current.id)

                const tracked_notebook = current.content;
                tracked_notebook.activeCellIndex = index;

                const activeCell = tracked_notebook.activeCell;

                NotebookActions.changeCellType(tracked_notebook, cellType);


                if (tracked_notebook.mode != "edit") {
                    tracked_notebook.activate();
                    tracked_notebook.mode = 'edit';
                }


                activeCell.model.sharedModel.setSource(args["content"]);

                if (activeCell instanceof MarkdownCell) {
                    activeCell.rendered = true;
                    return "ok"
                } else {
                    if (!(streaming)) {
                        await current.context.save();
                        const ststus = await NotebookActions.run(tracked_notebook, current.sessionContext)
                        const executionOutput = await functions["getCellOutput"].func({
                            index: index
                        })
                        return executionOutput
                    } else {
                        return "ok"
                    }
                }
            } catch (error) {
                return JSON.stringify({
                    error: `Error editing cell: ${error.message}`
                });

            }
        }
    }
    functions["executeCell"] = {
        "def": {
            "name": "executeCell",
            "description": "Execute a cell by index",
            "arguments": {
                "index": {
                    "type": "integer",
                    "name": "Index of the cell to execute"
                }
            }
        },
        "func": async (args: any): Promise<string> => {
            var { index } = args;
            index = typeof index === "string" ? parseInt(index, 10) : index;

            const current = notebookTracker.currentWidget

            app.shell.activateById(current.id)

            const tracked_notebook = current.content;

            tracked_notebook.activeCellIndex = index;
            const activeCell = tracked_notebook.activeCell;


            if (activeCell instanceof MarkdownCell) {
                activeCell.rendered = true;
                return "ok"
            } else {
                const ststus = await NotebookActions.run(tracked_notebook, current.sessionContext)
                const executionOutput = await functions["getCellOutput"].func({
                    index: index
                })
                return executionOutput
            }

        }
    }

    functions["getCellOutput"] = {
        "def": {
            "name": "getCellOutput",
            "description": "Get the output of a cell by index",
            "arguments": {
                "index": {
                    "type": "integer",
                    "name": "Index of the cell to get output from"
                }
            }
        },
        "func": async (args: any): Promise<any> => {
            var { index } = args;
            index = typeof index === "string" ? parseInt(index, 10) : index;

            const current = notebookTracker.currentWidget

            app.shell.activateById(current.id)

            const tracked_notebook = current.content;

            tracked_notebook.activeCellIndex = index;
            const activeCell = tracked_notebook.activeCell;

            if (activeCell instanceof CodeCell) {
                const outputArea = activeCell.outputArea;
                const outputs = [];
                for (let i = 0; i < outputArea.model.length; i++) {
                    const output = outputArea.model.get(i);
                    console.log(Array.isArray(output), output)
                    console.log(JSON.stringify(output))
                    outputs.push(output);
                }
                return outputs;
            } else {
                return "markdown cells do not have outputs"
            }

        }

    }

    functions["listCells"] = {
        "def": {
            "name": "listCells",
            "description": "Lists all cells in the active notebook with their content, type, and outputs",
            "arguments": {}
        },
        "func": async (args: any): Promise<any> => {
            const current = notebookTracker.currentWidget;
            if (current == undefined) {
                return []
            }
            const content = current.content;
            const notebook = notebookTracker.currentWidget.content;
            const cellsInfo = [];

            for (let i = 0; i < notebook.widgets.length; i++) {
                const cellWidget = notebook.widgets[i];
                const model = cellWidget.model;
                const type = model.type;
                const content = model.sharedModel.getSource();

                const cellInfo: any = {
                    index: i,
                    type: type,
                    content: content
                };

                if (cellWidget instanceof CodeCell) {
                    const outputArea = cellWidget.outputArea;
                    const outputs = [];

                    for (let j = 0; j < outputArea.model.length; j++) {
                        const output = outputArea.model.get(j);
                        outputs.push(output);
                    }
                    cellInfo.outputs = outputs;
                }
                cellsInfo.push(cellInfo);
            }
            return cellsInfo;
        }
    }

    /*
    functions["listCells"] = {
        "def": {
            "name": "listCells",
            "description": "Lists all cells in the active notebook with their content and type",
            "arguments": {}
        },
        "func": async (args: any): Promise<string> => {
            if (!app) {
                return JSON.stringify({ error: "JupyterLab app not initialized" });
            }
            // Damn Typescript :)
            const widget = app.shell.currentWidget;

            if (!(widget instanceof NotebookPanel)) {
                console.log(`-------------------CELLS ERROR! ${widget}`);
                return JSON.stringify({ error: "Type error reding cells from notebook - is it currently open??" });

            }

            const notebookPanel = widget as unknown as NotebookPanel;
            const notebook = notebookPanel.content;

            const cellsInfo = [];

            for (let i = 0; i < notebook.widgets.length; i++) {
                const cellWidget = notebook.widgets[i] as Cell;
                const model = cellWidget.model as CellModel;
                const type = model.type;
                const content = model.sharedModel.getSource();

                cellsInfo.push({
                    index: i,
                    type: type,
                    content: content
                });
            }
            return JSON.stringify(cellsInfo);
        }
    }
    */

    functions["deleteCell"] = {
        "def": {
            "name": "deleteCell",
            "description": "Delete a cell by index",
            "arguments": {
                "index": {
                    "type": "integer",
                    "name": "Index of the cell to delete"
                }
            }
        },
        "func": async (args: any): Promise<string> => {
            if (!app) {
                return JSON.stringify({ error: "JupyterLab app not initialized" });
            }

            const { index } = args;
            const notebook = getActiveNotebook(app);

            if (!notebook || !notebook.content) {
                return JSON.stringify({ error: "No active notebook found" });
            }

            if (!validateCellIndex(notebook, index)) {
                return JSON.stringify({ error: `Invalid cell index: ${index}` });
            }

            try {
                // Select the cell to delete
                notebook.content.activeCellIndex = index;

                // Delete the cell using NotebookActions
                NotebookActions.deleteCells(notebook.content);

                return JSON.stringify({
                    success: true,
                    message: `Cell at index ${index} deleted`
                });
            } catch (error) {
                return JSON.stringify({
                    error: `Error deleting cell: ${error.message}`
                });
            }
        }
    }


}
