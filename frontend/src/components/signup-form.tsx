"use client";

import { useEffect, useRef, useState } from "react";
import { signup, SignupError } from "@/lib/api";
import type { FieldErrors, SignupFields } from "@/types/auth";

const emptyFields: SignupFields = { name: "", email: "", password: "", password_confirmation: "" };
const labels: Record<keyof SignupFields, string> = {
  name: "이름", email: "이메일", password: "비밀번호", password_confirmation: "비밀번호 확인",
};

function Eye({ visible }: { visible: boolean }) {
  return <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" aria-hidden="true">
    <path d="M2 12s3.5-7 10-7 10 7 10 7-3.5 7-10 7S2 12 2 12Z" /><circle cx="12" cy="12" r="3" />
    {visible && <path d="m3 3 18 18" />}
  </svg>;
}

function validate(fields: SignupFields): FieldErrors {
  const errors: FieldErrors = {};
  const nameLength = Array.from(fields.name.trim()).length;
  if (nameLength < 2 || nameLength > 50) errors.name = "이름은 2~50자로 입력해 주세요.";
  if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(fields.email.trim())) errors.email = "올바른 이메일 주소를 입력해 주세요.";
  const passwordLength = Array.from(fields.password).length;
  if (passwordLength < 12 || passwordLength > 128 || !fields.password.trim()) {
    errors.password = "비밀번호는 공백만 사용하지 않고 12~128자로 입력해 주세요.";
  }
  if (!fields.password_confirmation || fields.password !== fields.password_confirmation) {
    errors.password_confirmation = "비밀번호가 일치하지 않습니다.";
  }
  return errors;
}

export function SignupForm() {
  const [fields, setFields] = useState<SignupFields>(emptyFields);
  const [errors, setErrors] = useState<FieldErrors>({});
  const [message, setMessage] = useState("");
  const [pending, setPending] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const [success, setSuccess] = useState(false);
  const submitting = useRef(false);
  const focusRequested = useRef(false);
  const formRef = useRef<HTMLFormElement>(null);

  useEffect(() => {
    if (focusRequested.current && !pending) {
      focusRequested.current = false;
      const key = Object.keys(errors)[0];
      if (key) (formRef.current?.elements.namedItem(key) as HTMLInputElement | null)?.focus();
    }
  }, [errors, pending]);

  function update(key: keyof SignupFields, value: string) {
    setFields(current => ({ ...current, [key]: value }));
    setErrors(current => ({ ...current, [key]: undefined }));
    setMessage("");
  }

  function focusFirstError(nextErrors: FieldErrors) {
    const key = Object.keys(nextErrors)[0];
    if (key) (formRef.current?.elements.namedItem(key) as HTMLInputElement | null)?.focus();
  }

  async function submit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (submitting.current) return;
    const nextErrors = validate(fields);
    setErrors(nextErrors);
    setMessage("");
    if (Object.keys(nextErrors).length) {
      focusFirstError(nextErrors);
      return;
    }
    submitting.current = true;
    setPending(true);
    try {
      await signup({ ...fields, name: fields.name.trim(), email: fields.email.trim() });
      setFields(emptyFields);
      setShowPassword(false);
      setSuccess(true);
    } catch (error) {
      if (error instanceof SignupError) {
        setErrors(error.fields);
        setMessage(error.message);
        focusRequested.current = true;
      } else {
        setMessage("가입 중 문제가 발생했습니다. 잠시 후 다시 시도해 주세요.");
      }
    } finally {
      submitting.current = false;
      setPending(false);
    }
  }

  if (success) {
    return <div className="success-panel" role="status" aria-live="polite">
      <div className="success-mark" aria-hidden="true">✓</div>
      <span className="eyebrow form-eyebrow">WELCOME TO MOA</span>
      <h2>반가워요,<br />이제 모아의 멤버예요.</h2>
      <p>회원가입이 완료되었습니다.<br />함께할 새로운 시작을 기대할게요.</p>
      <div className="success-info"><span aria-hidden="true">✓</span> 회원정보가 안전하게 저장되었습니다.</div>
      <button className="submit-button" onClick={() => { setSuccess(false); setErrors({}); setMessage(""); }}>가입 화면으로 돌아가기 <span aria-hidden="true">↗</span></button>
    </div>;
  }

  return <>
    <header className="form-heading">
      <span className="eyebrow form-eyebrow">JOIN OUR NEXT CHAPTER</span>
      <h2>모아와 함께 시작하기</h2>
      <p>간단한 정보만 입력하면 준비가 끝나요.</p>
    </header>
    <form ref={formRef} onSubmit={submit} noValidate aria-busy={pending}>
      <fieldset disabled={pending}>
        {(Object.keys(labels) as (keyof SignupFields)[]).map(key => {
          const isPassword = key === "password" || key === "password_confirmation";
          const error = errors[key];
          return <div className="field" key={key}>
            <label htmlFor={key}>{labels[key]} <span className="required-mark" aria-hidden="true">*</span></label>
            <div className={`input-wrap ${error ? "has-error" : ""}`}>
              <input
                id={key} name={key} required
                type={isPassword ? (showPassword ? "text" : "password") : key === "email" ? "email" : "text"}
                autoComplete={isPassword ? "new-password" : key}
                autoCapitalize={key === "email" ? "none" : undefined}
                spellCheck={key === "name" ? undefined : false}
                value={fields[key]} onChange={event => update(key, event.target.value)}
                maxLength={key === "name" ? 100 : key === "email" ? 254 : 256}
                placeholder={key === "name" ? "이름을 입력해 주세요" : key === "email" ? "hello@example.com" : key === "password" ? "12자 이상의 비밀번호" : "비밀번호를 한 번 더 입력해 주세요"}
                aria-invalid={Boolean(error)}
                aria-describedby={error ? `${key}-error` : key === "password" ? "password-help" : undefined}
              />
              {key === "password" && <button type="button" className="eye-button" aria-label={showPassword ? "비밀번호 숨기기" : "비밀번호 보기"} aria-pressed={showPassword} onClick={() => setShowPassword(value => !value)}><Eye visible={showPassword} /></button>}
            </div>
            {error && <p className="field-error" id={`${key}-error`} role="alert">{error}</p>}
            {key === "password" && !error && <p className="field-hint" id="password-help">12~128자로, 나만 알 수 있는 긴 비밀번호를 사용해 주세요.</p>}
          </div>;
        })}
        <details className="privacy-note"><summary>입력한 정보는 어떻게 사용되나요?</summary><p>이름과 이메일은 회원 식별을 위해 암호화하여 저장합니다. 비밀번호는 원문을 저장하지 않고 복원할 수 없는 해시로 저장합니다.</p></details>
        {message && <div className="form-error" role="alert">{message}</div>}
        <button className="submit-button" type="submit" disabled={pending}>{pending ? <><span className="spinner" aria-hidden="true" /> 가입하는 중이에요</> : <>회원가입 <span aria-hidden="true">↗</span></>}</button>
      </fieldset>
      <p className="safe-note"><svg viewBox="0 0 16 16" width="14" height="14" fill="none" stroke="currentColor" aria-hidden="true"><rect x="3" y="7" width="10" height="7" rx="2" /><path d="M5 7V5a3 3 0 0 1 6 0v2" /></svg> 소중한 개인정보, 안전하게 지킬게요.</p>
    </form>
  </>;
}
