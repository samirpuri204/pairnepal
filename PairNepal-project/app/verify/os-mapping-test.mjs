/**
 * Verifies the per-OS icon and OS-label mapping that PeerUI actually ships.
 *
 * The two method bodies are lifted out of app/public/scripts/ui.js as source
 * text and evaluated, so this tests the shipped code rather than a copy of it.
 * Every icon id the mapping can return is then checked against the <symbol>
 * definitions in index.html — an id with no symbol would render a blank tile.
 */
import fs from "fs";

const UI = "public/scripts/ui.js";
const HTML = "public/index.html";

const src = fs.readFileSync(UI, "utf8");

function body(method) {
    // Anchor on the definition, not a call site — `this._icon()` appears
    // earlier in the file and would silently yield the wrong method.
    const def = new RegExp("^\\s*" + method + "\\(\\)\\s*\\{", "m").exec(src);
    if (!def) throw new Error(`definition of ${method}() not found in ${UI}`);
    const start = def.index;
    let i = src.indexOf("{", start);
    let depth = 0;
    for (let j = i; j < src.length; j++) {
        if (src[j] === "{") depth++;
        else if (src[j] === "}") {
            depth--;
            if (depth === 0) return src.slice(i + 1, j);
        }
    }
    throw new Error(`unbalanced braces for ${method}`);
}

const _icon = new Function("return function " + "_icon" + "()" + "{" + body("_icon") + "}")();
const _osName = new Function("return function " + "_osName" + "()" + "{" + body("_osName") + "}")();

const CASES = [
    // [peer name object, expected icon, expected full OS label]
    [{ os: "Mac OS" }, "#os-apple", "macOS"],
    [{ os: "macOS" }, "#os-apple", "macOS"],
    [{ os: "iOS" }, "#os-apple", "iOS"],
    [{ os: "Windows" }, "#os-windows", "Windows"],
    [{ os: "Windows Phone" }, "#os-windows", "Windows Phone"],
    [{ os: "Android" }, "#os-android", "Android"],
    [{ os: "Android-Android" }, "#os-android", "Android"],
    [{ os: "Chrome OS" }, "#os-chrome", "ChromeOS"],
    [{ os: "Chromium OS" }, "#os-chrome", "ChromeOS"],
    [{ os: "Ubuntu" }, "#os-ubuntu", "Ubuntu"],
    [{ os: "Linux" }, "#os-linux", "Linux"],
    [{ os: "Fedora" }, "#os-linux", "Fedora"],
    [{ os: "Debian" }, "#os-linux", "Debian"],
    // No OS reported: fall back to the device class, never blank.
    [{ os: "", device: { type: "mobile" } }, "#phone-iphone", "Mobile"],
    [{ os: "", device: { type: "tablet" } }, "#tablet-mac", "Tablet"],
    [{ os: "", device: { type: undefined } }, "#desktop-mac", "Desktop"],
    [{}, "#desktop-mac", "Desktop"],
];

let fail = 0;
console.log(`${"os".padEnd(18)} ${"icon".padEnd(16)} ${"label".padEnd(14)}`);
console.log("-".repeat(58));
for (const [name, wantIcon, wantLabel] of CASES) {
    const self = { _peer: { name } };
    let icon, label;
    try {
        icon = _icon.call(self);
        label = _osName.call(self);
    } catch (e) {
        console.log(`${String(name.os || "(none)").padEnd(18)} THREW ${e.message}`);
        fail++;
        continue;
    }
    const ok = icon === wantIcon && label === wantLabel;
    if (!ok) fail++;
    console.log(
        `${String(name.os || "(none)").padEnd(18)} ${icon.padEnd(16)} ${label.padEnd(14)} ${ok ? "" : `  << want ${wantIcon} / ${wantLabel}`}`
    );
}

// Every icon id must have a matching <symbol>, or the tile renders empty.
const html = fs.readFileSync(HTML, "utf8");
const symbols = new Set([...html.matchAll(/<symbol id="([^"]+)"/g)].map(m => "#" + m[1]));
const used = new Set(CASES.map(c => c[1]));
for (const id of used) {
    if (!symbols.has(id)) {
        console.log(`MISSING SYMBOL in index.html: ${id}`);
        fail++;
    }
}

console.log("-".repeat(58));
console.log(`checked ${CASES.length} mappings, ${used.size} distinct icons`);
console.log(fail === 0 ? "PASS - every OS maps to a real icon and a full label"
                       : `FAIL - ${fail} problem(s)`);
process.exit(fail === 0 ? 0 : 1);
