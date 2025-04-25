import * as monaco from 'monaco-editor';
import 'monaco-editor/min/vs/editor/editor.main.css';  // Monaco core styles
import 'monaco-editor/esm/vs/editor/contrib/find/browser/findOptionsWidget.css';  // For find options widget
import 'monaco-editor/'

// Step 1: Create Monaco Editor
function createCodeEditor() {
    return monaco.editor.create(document.getElementById('editorContainerProcessing'), {
        value: "",
        language: 'python',
        theme: 'vs-dark',
        automaticLayout: true,
    });
}

const processingEditor = createCodeEditor();
window.processingEditor = processingEditor;
