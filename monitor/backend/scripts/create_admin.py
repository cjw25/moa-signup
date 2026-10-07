import getpass

from werkzeug.security import generate_password_hash

from db import connect_db


def main():
    username = input("아이디: ").strip()
    display_name = input("표시 이름: ").strip()
    password = getpass.getpass("비밀번호: ")
    if not username or not display_name or not password.strip():
        raise SystemExit("모든 값을 입력해 주세요.")
    with connect_db() as conn:
        conn.execute(
            "INSERT INTO monitor_users (username, display_name, password_hash) "
            "VALUES (%s, %s, %s)",
            (username, display_name, generate_password_hash(password)),
        )
    print("관리자 계정을 만들었습니다.")


if __name__ == "__main__":
    main()
