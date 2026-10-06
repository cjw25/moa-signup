import type { FieldErrors, SignupFields, SignupResult } from "@/types/auth";

export class SignupError extends Error {
  constructor(message: string, public fields: FieldErrors = {}) {
    super(message);
    this.name = "SignupError";
  }
}

export async function signup(fields: SignupFields): Promise<SignupResult> {
  let response: Response;
  try {
    response = await fetch("/api/auth/signup", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(fields),
      cache: "no-store",
      signal: AbortSignal.timeout(15000),
    });
  } catch {
    throw new SignupError("서버에 연결하지 못했습니다. 잠시 후 다시 시도해 주세요.");
  }

  const data = await response.json().catch(() => null);
  if (!response.ok) {
    throw new SignupError(
      response.status >= 500
        ? "서버에 연결하지 못했습니다. 잠시 후 다시 시도해 주세요."
        : data?.message || "회원가입을 완료하지 못했습니다. 다시 시도해 주세요.",
      data?.errors || {},
    );
  }
  if (!data?.id) throw new SignupError("서버 응답을 확인하지 못했습니다. 다시 시도해 주세요.");
  return data as SignupResult;
}
