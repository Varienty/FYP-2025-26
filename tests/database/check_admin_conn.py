from common import db_utils

def main():
    print("Testing db_utils connection and fetching system_admins row...")
    row = db_utils.query_one("SELECT id, admin_id, email, password FROM system_admins WHERE email=%s", ("haha@gmail.com",))
    print("Result:", row)

if __name__ == "__main__":
    main()