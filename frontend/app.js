/**
 * AWS URL Shortener - Frontend Client
 * Configura la URL base de tu backend desplegado en EC2 aquí:
 */
const API_BASE_URL = "http://3.91.243.55:8000";

// Elementos del DOM
const shortenForm = document.getElementById("shorten-form");
const urlInput = document.getElementById("url-input");
const submitBtn = document.getElementById("submit-btn");
const errorBox = document.getElementById("error-box");
const errorMessage = document.getElementById("error-message");
const resultBox = document.getElementById("result-box");
const shortUrlOutput = document.getElementById("short-url-output");
const copyBtn = document.getElementById("copy-btn");
const copyBtnText = document.getElementById("copy-btn-text");
const shortCodeLabel = document.getElementById("short-code-label");
const testLink = document.getElementById("test-link");

/**
 * Valida si la cadena ingresada es una URL válida con protocolo HTTP/HTTPS.
 */
function isValidUrl(urlString) {
  try {
    const parsed = new URL(urlString);
    return parsed.protocol === "http:" || parsed.protocol === "https:";
  } catch (_) {
    return false;
  }
}

/**
 * Muestra el contenedor de error con un mensaje específico.
 */
function showError(message) {
  errorMessage.textContent = message;
  errorBox.hidden = false;
  resultBox.hidden = true;
}

/**
 * Limpia y oculta los mensajes de error.
 */
function hideError() {
  errorBox.hidden = true;
  errorMessage.textContent = "";
}

/**
 * Gestiona el estado de carga del botón principal.
 */
function setLoading(isLoading) {
  if (isLoading) {
    submitBtn.classList.add("loading");
    submitBtn.disabled = true;
    submitBtn.querySelector(".btn-text").textContent = "Acortando enlace...";
  } else {
    submitBtn.classList.remove("loading");
    submitBtn.disabled = false;
    submitBtn.querySelector(".btn-text").textContent = "Acortar URL";
  }
}

// Envío del formulario
shortenForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  hideError();

  const rawUrl = urlInput.value.trim();

  // Validación en cliente
  if (!rawUrl) {
    showError("Por favor ingresa una URL.");
    urlInput.focus();
    return;
  }

  if (!isValidUrl(rawUrl)) {
    showError("Ingresa una URL válida que comience con http:// o https://");
    urlInput.focus();
    return;
  }

  setLoading(true);

  try {
    const response = await fetch(`${API_BASE_URL}/shorten`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ original_url: rawUrl }),
    });

    if (!response.ok) {
      let detailMsg = `Error ${response.status}: no se pudo procesar la solicitud.`;
      try {
        const errorData = await response.json();
        if (errorData.detail) {
          if (Array.isArray(errorData.detail)) {
            detailMsg = errorData.detail.map((err) => err.msg).join(", ");
          } else {
            detailMsg = errorData.detail;
          }
        }
      } catch (_) {}
      throw new Error(detailMsg);
    }

    const data = await response.json();

    // Renderizar resultado
    shortUrlOutput.value = data.short_url;
    shortCodeLabel.textContent = data.short_code;
    testLink.href = data.short_url;
    resultBox.hidden = false;

    // Scroll hacia el resultado en pantallas pequeñas
    resultBox.scrollIntoView({ behavior: "smooth", block: "nearest" });
  } catch (error) {
    showError(error.message || "No fue posible conectar con el servidor backend en EC2.");
  } finally {
    setLoading(false);
  }
});

// Función de copiado al portapapeles
copyBtn.addEventListener("click", async () => {
  if (!shortUrlOutput.value) return;

  try {
    await navigator.clipboard.writeText(shortUrlOutput.value);
    copyBtn.classList.add("copied");
    copyBtnText.textContent = "¡Copiado!";

    setTimeout(() => {
      copyBtn.classList.remove("copied");
      copyBtnText.textContent = "Copiar";
    }, 2500);
  } catch (err) {
    // Fallback tradicional si falla la API Clipboard
    shortUrlOutput.select();
    document.execCommand("copy");
    copyBtnText.textContent = "¡Copiado!";
    setTimeout(() => {
      copyBtnText.textContent = "Copiar";
    }, 2500);
  }
});
