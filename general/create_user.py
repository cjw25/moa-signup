import getpass

from werkzeug.security import generate_password_hash

from db import connect_db


def main():
    username = input("아이디: ").strip()
    password = getpass.getpass("비밀번호: ")
    if not username or not password.strip():
        raise SystemExit("아이디와 비밀번호를 입력해 주세요.")
    with connect_db() as conn:
        conn.execute(
            "INSERT INTO general_users (username, password_hash) VALUES (%s, %s) "
            "ON CONFLICT (username) DO UPDATE SET password_hash = EXCLUDED.password_hash",
            (username, generate_password_hash(password)),
        )
    print("게시판 계정을 저장했습니다.")


if __name__ == "__main__":
    main()
