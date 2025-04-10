app.alert("welcome to pdfboy")
var Module = {};

Module.print = function (e) {
    app.alert(e)
}
Module.printErr = function (e) {
    app.alert(e)
}

// --- ROM Loading
var b64rom = "__replace_with_rom__";

// Base64 functions are not available in a PDF
function base64ToUint8Array(base64) {
	const base64Chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/";
	const base64Map = Object.fromEntries(base64Chars.split("").map((char, index) => [char, index]));

	const cleanedBase64 = base64.replace(/=+$/, "");
	if (cleanedBase64.length % 4 === 1) {
		throw new Error("Invalid Base64 string");
	}

	const outputLength = Math.floor((cleanedBase64.length * 3) / 4);
	const buffer = new Uint8Array(outputLength);

	let bufferIndex = 0;
	for (let i = 0; i < cleanedBase64.length; i += 4) {
		const encoded1 = base64Map[cleanedBase64[i]] ?? 0;
		const encoded2 = base64Map[cleanedBase64[i + 1]] ?? 0;
		const encoded3 = base64Map[cleanedBase64[i + 2]] ?? 0;
		const encoded4 = base64Map[cleanedBase64[i + 3]] ?? 0;

		const byte1 = (encoded1 << 2) | (encoded2 >> 4);
		const byte2 = ((encoded2 & 15) << 4) | (encoded3 >> 2);
		const byte3 = ((encoded3 & 3) << 6) | encoded4;

		buffer[bufferIndex++] = byte1;
		if (bufferIndex < outputLength) buffer[bufferIndex++] = byte2;
		if (bufferIndex < outputLength) buffer[bufferIndex++] = byte3;
	}

	return buffer;
}

function loadROMToFS() {
	// Decodes ROM data and places it into the VFS
	let stream = FS.open("/" + 'rom.gb', "w+"); // rom.gb is the generic name to transfer to C
	const uint8Buffer = base64ToUint8Array(b64rom);

	FS.write(stream, uint8Buffer, 0, uint8Buffer.length, 0);
	FS.close(stream);

	Module.print("ROM decoded and placed in FS");
}