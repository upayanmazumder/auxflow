import * as assert from 'node:assert/strict';
import * as path from 'node:path';
import * as vscode from 'vscode';

async function eventually(predicate: () => boolean, description: string): Promise<void> {
    for (let attempt = 0; attempt < 100; attempt++) {
        if (predicate()) {
            return;
        }
        await new Promise<void>((resolve) => setTimeout(resolve, 100));
    }
    assert.fail(`Timed out waiting for ${description}`);
}

export async function run(): Promise<void> {
    const workspace = vscode.workspace.workspaceFolders?.[0];
    assert.ok(workspace, 'test host must open the fixture workspace');
    const main = vscode.Uri.file(path.join(workspace.uri.fsPath, 'main.tex'));
    const child = vscode.Uri.file(path.join(workspace.uri.fsPath, 'child.tex'));
    const config = vscode.workspace.getConfiguration('auxflow', main);
    await config.update('mainFile', 'main.tex', vscode.ConfigurationTarget.Workspace);
    await config.update('debounceMilliseconds', 25, vscode.ConfigurationTarget.Workspace);
    const extension = vscode.extensions.getExtension('UpayanMazumder.auxflow');
    assert.ok(extension);
    await vscode.window.showTextDocument(await vscode.workspace.openTextDocument(main));
    await extension.activate();
    await eventually(
        () =>
            vscode.languages
                .getDiagnostics(main)
                .some(
                    (diagnostic) =>
                        diagnostic.source === 'AuxFlow' &&
                        diagnostic.message.includes("undefined reference: 'absent'"),
                ),
        'initial main-file diagnostic',
    );

    const document = await vscode.workspace.openTextDocument(child);
    await vscode.window.showTextDocument(document);
    const edit = new vscode.WorkspaceEdit();
    edit.replace(
        child,
        new vscode.Range(document.positionAt(0), document.positionAt(document.getText().length)),
        '\\ref{missing}\n',
    );
    assert.ok(await vscode.workspace.applyEdit(edit));
    await eventually(
        () =>
            vscode.languages
                .getDiagnostics(child)
                .some(
                    (diagnostic) =>
                        diagnostic.source === 'AuxFlow' &&
                        diagnostic.message.includes("undefined reference: 'missing'"),
                ),
        'unsaved included-file diagnostic',
    );
    assert.equal(document.isDirty, true);
    const entry = vscode.languages
        .getDiagnostics(child)
        .find((diagnostic) => diagnostic.source === 'AuxFlow');
    assert.ok(entry);
    assert.equal(entry.range.start.line, 0);
    assert.equal(entry.range.end.character, 13);
    assert.ok(vscode.languages.getDiagnostics(main).some((diagnostic) => diagnostic.source === 'AuxFlow'));

    await config.update(
        'pythonPath',
        '/this/path/does/not/exist/auxflow-python',
        vscode.ConfigurationTarget.Workspace,
    );
    await eventually(
        () => vscode.languages.getDiagnostics(main).every((diagnostic) => diagnostic.source !== 'AuxFlow'),
        'stale diagnostics cleared after interpreter failure',
    );
    assert.deepEqual(
        vscode.languages.getDiagnostics(child).filter((d) => d.source === 'AuxFlow'),
        [],
        'failure must not preserve stale diagnostics',
    );
    await config.update('pythonPath', 'python3', vscode.ConfigurationTarget.Workspace);
    await eventually(
        () => vscode.languages.getDiagnostics(child).some((d) => d.source === 'AuxFlow'),
        'recovery after interpreter failure',
    );

    await vscode.commands.executeCommand('workbench.action.files.revert');
    await vscode.commands.executeCommand('workbench.action.closeActiveEditor');
    await eventually(
        () => vscode.languages.getDiagnostics(child).every((d) => d.source !== 'AuxFlow'),
        'diagnostics cleared on close',
    );
    await config.update('mainFile', '', vscode.ConfigurationTarget.Workspace);
}
