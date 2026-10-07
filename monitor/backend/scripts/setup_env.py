from pathlib import Path
import secrets


def main():
    backend = Path(__file__).resolve().parents[1]
    env_path = backend / ".env"
    if not env_path.exists():
        raise SystemExit("먼저 .env.example을 .env로 복사해 주세요.")
    content = env_path.read_text(encoding="utf-8")
    marker = "REPLACE_WITH_A_LONG_RANDOM_HEX_VALUE"
    if marker in content:
        env_path.write_text(content.replace(marker, secrets.token_hex(32)), encoding="utf-8")
        print("세션 비밀 키를 생성했습니다. DATABASE_URL도 확인해 주세요.")
    else:
        print("기존 세션 비밀 키를 유지했습니다.")


if __name__ == "__main__":
    main()
