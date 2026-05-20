from app import app
from models import db, User, Task
from datetime import datetime, timedelta


def populate_database():
    with app.app_context():
        # Clear existing data
        db.drop_all()
        db.create_all()

        print("Creating users...")
        # Create admin user
        admin = User(username='admin', password='admin123', is_admin=True)
        db.session.add(admin)

        # Create regular users
        users = [
            User(username='john', password='password123'),
            User(username='alice', password='securepass'),
            User(username='bob', password='bobpassword'),
            User(username='susan', password='susan1234'),
            User(username='mike', password='mikepass')
        ]

        for user in users:
            db.session.add(user)

        db.session.commit()
        print("Users created successfully!")

        print("Creating tasks...")
        # Sample task descriptions with various content
        descriptions = [
            "Complete the project documentation by Friday.",
            "Call the client to discuss requirements.",
            "<b>Important:</b> Submit the expense report.",
            "Research new technologies for upcoming project.",
            "Prepare presentation for team meeting.",
            "<script>alert('XSS Test')</script>",
            "Follow up with marketing about campaign launch.",
            "Fix bugs in login functionality.",
            "Update website content with new information.",
            "Review pull requests from team members."
        ]

        # Create tasks for each user
        all_users = User.query.all()
        for i, user in enumerate(all_users):
            # Each user gets 3-5 tasks
            num_tasks = 3 + (i % 3)
            for j in range(num_tasks):
                desc_index = (i + j) % len(descriptions)
                days_ago = (i * 2) + j

                task = Task(
                    title=f"Task {j + 1} for {user.username}",
                    description=descriptions[desc_index],
                    created_at=datetime.utcnow() - timedelta(days=days_ago),
                    completed=(j % 3 == 0),  # Every third task is completed
                    user_id=user.id
                )
                db.session.add(task)

        db.session.commit()
        print("Tasks created successfully!")

        print("Database populated with test data!")
        print("\nAdmin account:")
        print("Username: admin")
        print("Password: admin123")

        print("\nRegular user accounts (sample):")
        print("Username: john, Password: password123")
        print("Username: alice, Password: securepass")


if __name__ == "__main__":
    populate_database()