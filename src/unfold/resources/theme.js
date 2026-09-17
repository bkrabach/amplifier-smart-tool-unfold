// Apply the browser preference before first paint; System follows live OS changes via CSS.
window.unfoldTheme = (mode, persist = false) => {
  mode = ["light", "dark"].includes(mode) ? mode : "system";
  if (mode === "system") delete document.documentElement.dataset.theme;
  else document.documentElement.dataset.theme = mode;
  if (persist) {
    try {
      localStorage.setItem("unfold.theme", mode);
    } catch {}
  }
  return mode;
};
try {
  window.unfoldTheme(localStorage.getItem("unfold.theme"));
} catch {
  window.unfoldTheme("system");
}
