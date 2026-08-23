export const TEXTAREA_INITIAL_HEIGHT = 56

export function autoResizeTextarea(el, value, initialHeight = TEXTAREA_INITIAL_HEIGHT) {
  if (!el) return
  if (!value) {
    el.style.height = `${initialHeight}px`
    return
  }
  el.style.height = 'auto'
  el.style.height = `${el.scrollHeight}px`
}
