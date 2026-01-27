import sys
import getpass
from sqlmodel import Session, select
from app.models.database import engine, User
from app.core.security import get_password_hash

def reset_password():
    print("--- s-panel Password Reset Tool ---")
    
    # default to admin if no arg provided
    target_username = sys.argv[1] if len(sys.argv) > 1 else "admin"
    
    with Session(engine) as session:
        statement = select(User).where(User.username == target_username)
        user = session.exec(statement).first()
        
        if not user:
            print(f"Error: User '{target_username}' not found.")
            return

        print(f"Resetting password for user: {target_username}")
        
        while True:
            new_password = getpass.getpass("Enter new password: ")
            confirm_password = getpass.getpass("Confirm new password: ")
            
            if new_password == confirm_password:
                break
            print("Passwords do not match. Please try again.")

        if not new_password:
             print("Password cannot be empty.")
             return

        user.password_hash = get_password_hash(new_password)
        session.add(user)
        session.commit()
        session.refresh(user)
        
        print(f"\nSuccess! Password for '{target_username}' has been updated.")

if __name__ == "__main__":
    try:
        reset_password()
    except KeyboardInterrupt:
        print("\nOperation cancelled.")
    except Exception as e:
        print(f"\nAn error occurred: {e}")
