const fs = require('node:fs');
const path = require('node:path');

const source = path.resolve(__dirname, '../../src/auxflow');
const destination = path.resolve(__dirname, '../python/auxflow');
if (!fs.existsSync(path.join(source, 'cli.py'))) {
    throw new Error(`AuxFlow Python source not found at ${source}; package from the repository checkout.`);
}
fs.rmSync(destination, { recursive: true, force: true });
function copy(directory, target) {
    fs.mkdirSync(target, { recursive: true });
    for (const entry of fs.readdirSync(directory, { withFileTypes: true })) {
        if (entry.isDirectory()) {
            if (entry.name !== '__pycache__') {
                copy(path.join(directory, entry.name), path.join(target, entry.name));
            }
        } else if (entry.isFile() && entry.name.endsWith('.py') && entry.name !== '_version.py') {
            fs.copyFileSync(path.join(directory, entry.name), path.join(target, entry.name));
        }
    }
}
copy(source, destination);
