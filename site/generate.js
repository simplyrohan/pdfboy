const rom_file = document.getElementById("rom-file");
const open_btn = document.getElementById("open-btn");

/** @param {File} file */
function read_file_b64(file) {
    return new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.readAsDataURL(file);
        reader.onload = () => resolve(reader.result.split(",")[1]);
        reader.onerror = error => reject(error);
    });
}

/** 
 * @param {string} rom 
 * @returns {Blob} 
 */
async function generate() {
    let rom = await read_file_b64(rom_file.files[0])

    let pdf = await (await fetch("./norom.pdf")).text();
    pdf = pdf.replace("__replace_with_rom__", rom);

    return new Blob([pdf], { type: "application/pdf" });
}

rom_file.addEventListener("change", () => {
    if (rom_file.files.length != 0) {
        open_btn.disabled = false;
    }
    else {
        open_btn.disabled = true;
    }
})

open_btn.addEventListener("click", async () => {
    open(URL.createObjectURL(await generate()))
});