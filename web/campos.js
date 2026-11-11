// Campos reais sobre os cartões do Pygame: seleção, colagem e teclado do celular.
const camposCognit = new Map(
    [...document.querySelectorAll(".campo-cognit")].map(campo => [campo.dataset.campo, campo])
);
let camposAlterados = false;
let areasCampos = {};

function posicionar_campos() {
    const canvas = document.getElementById("canvas").getBoundingClientRect();
    const escalaX = canvas.width / 390;
    const escalaY = canvas.height / 844;
    for (const [nome, campo] of camposCognit) {
        const area = areasCampos[nome];
        if (campo.hidden || !area) continue;
        const [x, y, largura, altura] = area;
        Object.assign(campo.style, {
            left: `${canvas.left + x * escalaX}px`,
            top: `${canvas.top + y * escalaY}px`,
            width: `${largura * escalaX}px`,
            height: `${altura * escalaY}px`,
            fontSize: `${Math.max(16, 17 * Math.min(escalaX, escalaY))}px`,
            padding: `0 ${12 * escalaX}px`,
            borderRadius: `${14 * Math.min(escalaX, escalaY)}px`
        });
    }
}

function cognit_campos_exibir(serializado) {
    const dados = JSON.parse(serializado);
    areasCampos = {};
    for (const [nome, campo] of camposCognit) {
        const cadastro = dados[nome];
        if (!cadastro) {
            if (document.activeElement === campo) campo.blur();
            campo.hidden = true;
            continue;
        }
        areasCampos[nome] = cadastro.area;
        // Não reescreve o valor durante edição ou composição de acentos.
        if (document.activeElement !== campo && campo.value !== cadastro.valor) {
            campo.value = cadastro.valor;
        }
        campo.hidden = false;
    }
    posicionar_campos();
}

function cognit_campos_ocultar() {
    for (const campo of camposCognit.values()) {
        if (document.activeElement === campo) campo.blur();
        campo.hidden = true;
    }
    areasCampos = {};
}

function cognit_campos_ler() {
    if (!camposAlterados) return "";
    camposAlterados = false;
    return cognit_json_ascii({
        valores: Object.fromEntries([...camposCognit].map(([nome, campo]) => [nome, campo.value])),
        ativo: document.activeElement?.classList.contains("campo-cognit")
            ? document.activeElement.dataset.campo : null
    });
}

function cognit_campo_focar(nome) {
    const campo = camposCognit.get(nome);
    if (campo && !campo.hidden) campo.focus({preventScroll: true});
}

function filtrar_campo(campo) {
    const anterior = campo.value;
    const filtrar = valor => campo.dataset.campo === "codigo"
        ? valor.replace(/[^0-9]/g, "").slice(0, 6)
        : Array.from(valor.replace(/[\u0000-\u001f\u007f-\u009f]/g, "")).slice(0, 20).join("");
    const valor = filtrar(anterior);
    if (valor !== anterior) {
        const cursor = filtrar(anterior.slice(0, campo.selectionStart ?? anterior.length)).length;
        campo.value = valor;
        campo.setSelectionRange(cursor, cursor);
    }
    camposAlterados = true;
}

for (const campo of camposCognit.values()) {
    campo.addEventListener("input", evento => {
        if (!evento.isComposing) filtrar_campo(campo);
    });
    campo.addEventListener("compositionend", () => filtrar_campo(campo));
    campo.addEventListener("focus", () => { camposAlterados = true; });
    campo.addEventListener("blur", () => { camposAlterados = true; });
    campo.addEventListener("keydown", evento => {
        if (!evento.isComposing && (evento.key === "Enter" || evento.key === "Escape")) {
            evento.preventDefault();
            campo.blur();
            document.getElementById("canvas").focus({preventScroll: true});
        }
        evento.stopPropagation();
    });
    for (const tipo of ["keyup", "keypress", "pointerdown", "pointerup", "click", "touchstart", "touchend"]) {
        campo.addEventListener(tipo, evento => evento.stopPropagation());
    }
}
document.addEventListener("pointerdown", evento => {
    if (!evento.target.closest(".campo-cognit")
            && document.activeElement?.classList.contains("campo-cognit")) {
        document.activeElement.blur();
    }
}, true);
window.addEventListener("resize", posicionar_campos);
window.visualViewport?.addEventListener("resize", posicionar_campos);
window.visualViewport?.addEventListener("scroll", posicionar_campos);
