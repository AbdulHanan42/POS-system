export function required(value) {
  return Boolean(String(value ?? '').trim())
}
