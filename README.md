💡 LearnSphere — College Academic Management System
LearnSphere is a modern web application designed to streamline academic workflows for colleges and universities. The system offers separate, role-based dashboards for students, teachers, and administrators — while introducing AI-powered features for code explanation, code generation, and solving small math problems.

🚀 Features
🎓 Student Module
View and track attendance.

Access and submit assignments with real-time feedback.

Get instant support with AI-powered code explanation, code generation, and math-solving.

Receive notifications for important deadlines, class updates, and academic alerts.

Check results and performance summaries.

👨‍🏫 Teacher Module
Mark and manage attendance.

Create and distribute assignments and notes.

Send notifications to students and manage classroom updates.

🧑‍💼 Admin Module
Manage teacher and student accounts.

Assign roles and permissions.

Monitor platform usage and maintain data integrity.

🤖 Machine Learning Features
Code Explanation & Generation: Get code insights and generation for various programming languages.

Math Problem Solver: Solve small mathematical problems instantly.

Powered by Groq API and EasyOCR for intelligent and efficient responses.

💻 Tech Stack

Layer	Technology
Backend	Django
Frontend	HTML, CSS, JavaScript
Database	PostgreSQL / MySQL / SQLite
AI & Machine Learning	Groq API, EasyOCR

🔧 Setup Instructions
Clone the repo:

bash
Copy
Edit
git clone https://github.com/your-username/learnsphere.git
cd learnsphere
Create and activate a virtual environment:

bash
Copy
Edit
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
Install dependencies:

bash
Copy
Edit
pip install -r requirements.txt
Configure database and .env settings.

Apply migrations and run the server:

bash
Copy
Edit
python manage.py migrate
python manage.py runserver
🛡️ Security & Scalability
Role-based access control.

Centralized user management.

Secure handling of sensitive data.

Flexible to integrate new ML services and expand features.

🌱 Future Enhancements
Advanced AI-powered personalized study recommendations.

Virtual Reality (VR) based virtual campus tours.

Community forums for peer-to-peer discussion.

Environmental footprint insights for sustainable learning habits.

📚 References
Books, documentation, and online resources used during development are listed in the docs folder.

🤝 Contributing
Contributions are welcome! Feel free to fork the repo and submit a pull request.

📢 License
This project is open-source — MIT License.
