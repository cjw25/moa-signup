export async function api(path, options = {}) {
  let response
  try {
    response = await fetch(`/api${path}`, {
      ...options,
      headers: { 'Content-Type': 'application/json', ...options.headers },
      cache: 'no-store',
      credentials: 'same-origin',
    })
  } catch {
    throw new Error('서버에 연결하지 못했습니다.')
  }
  const data = response.status === 204 ? null : await response.json().catch(() => null)
  if (!response.ok) {
    const error = new Error(data?.message || `요청에 실패했습니다. (${response.status})`)
    error.status = response.status
    throw error
  }
  return data
}
