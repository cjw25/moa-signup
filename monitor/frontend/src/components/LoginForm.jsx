import { useState } from 'react'
import { login } from '../api/auth'

export default function LoginForm({ onLogin }) {
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [busy, setBusy] = useState(false)

  async function submit(event) {
    event.preventDefault()
    setError('')
    setBusy(true)
    try {
      const result = await login(username, password)
      onLogin(result.user)
    } catch (cause) {
      setError(cause.message)
    } finally {
      setBusy(false)
    }
  }

  return <main className="login card"><h1>Mini Watch</h1><p>운영자 로그인</p><form onSubmit={submit}>
    <label>아이디<input value={username} onChange={event => setUsername(event.target.value)} autoComplete="username" /></label>
    <label>비밀번호<input type="password" value={password} onChange={event => setPassword(event.target.value)} autoComplete="current-password" /></label>
    {error && <p className="error" role="alert">{error}</p>}
    <button disabled={busy}>{busy ? '확인 중...' : '로그인'}</button>
  </form></main>
}
