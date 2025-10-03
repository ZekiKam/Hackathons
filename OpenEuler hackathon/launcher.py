import os

def main():
    while True:
        print("\n=== OpenEuler System Monitor Launcher ===")
        print("1. Start Backend (metrics.py)")
        print("2. Start Frontend (npm run preview)")
        print("3. Stop Backend")
        print("4. Stop Frontend")
        print("5. Exit")
        choice = input("Select option: ").strip()

        if choice == "1":
            print("Starting backend...")
            os.system("cd ~/Hackathons/'OpenEuler hackathon'/backend && nohup python3 metrics.py > backend.log 2>&1 &")
        elif choice == "2":
            print("Starting frontend...")
            os.system("cd ~/Hackathons/'OpenEuler hackathon'/frontend && nohup npm run preview -- --host 0.0.0.0 --port 5173 > frontend.log 2>&1 &")
        elif choice == "3":
            print("Stopping backend...")
            os.system("pkill -f 'metrics.py'")
        elif choice == "4":
            print("Stopping frontend...")
            os.system("pkill -f 'vite' || pkill -f 'npm run preview'")
        elif choice == "5":
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Try again.")

if __name__ == "__main__":
    main()