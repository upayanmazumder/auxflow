import * as fs from 'node:fs';
import * as os from 'node:os';
import * as path from 'node:path';
import { runTests } from '@vscode/test-electron';

async function main(): Promise<void> {
    const extensionDevelopmentPath = path.resolve(__dirname, '../..');
    const extensionTestsPath = path.resolve(__dirname, 'suite/index');
    const workspace = fs.mkdtempSync(path.join(os.tmpdir(), 'auxflow-vscode-'));
    fs.writeFileSync(path.join(workspace, 'main.tex'), '\\input{child}\n\\ref{absent}\n');
    fs.writeFileSync(path.join(workspace, 'child.tex'), '\\label{known}\n');
    try {
        await runTests({
            extensionDevelopmentPath,
            extensionTestsPath,
            vscodeExecutablePath: process.env.AUXFLOW_TEST_CODE_PATH,
            launchArgs: [workspace, '--disable-workspace-trust', '--skip-welcome', '--skip-release-notes'],
        });
    } finally {
        fs.rmSync(workspace, { recursive: true, force: true });
    }
}

void main().catch((error) => {
    console.error(error);
    process.exitCode = 1;
});
