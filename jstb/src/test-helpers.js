export function deindent(s) {
	let m = s.match(/^[ \t]*(?=\S)/gm);
	if (!m)
		return s;

	let indent = Math.min.apply(Math, m.map((e) => e.length));
	let re = new RegExp("^[ \\t]{" + indent + "}", "gm");
	return (indent > 0) ? s.replace(re, "") : s;
}

