import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from analyzer.models import Branch, Skill, JobRole, RequiredSkill

data = [
    {
        "branch": "Computer Science and Engineering",
        "roles": [
            {"name": "Full Stack Developer", "skills": ["HTML", "CSS", "JavaScript", "React", "Node.js", "MongoDB", "SQL", "Git"]},
            {"name": "Mobile App Developer", "skills": ["Java", "Kotlin", "Swift", "Flutter", "React Native", "Android Studio"]},
            {"name": "UI/UX Designer", "skills": ["Figma", "Adobe XD", "User Research", "Wireframing", "Prototyping", "CSS"]},
            {"name": "DevOps Engineer", "skills": ["Linux", "Docker", "Kubernetes", "AWS", "CI/CD", "Jenkins", "Python"]},
            {"name": "QA Analyst", "skills": ["Manual Testing", "Automation Testing", "Selenium", "JIRA", "Python", "Java"]},
            {"name": "Game Developer", "skills": ["C++", "C#", "Unity", "Unreal Engine", "3D Math", "Game Design"]},
            {"name": "Cybersecurity Analyst", "skills": ["Networking", "Linux", "Ethical Hacking", "Cryptography", "Penetration Testing", "Security Protocols"]},
            {"name": "AI Engineer", "skills": ["Python", "TensorFlow", "PyTorch", "Machine Learning", "Deep Learning", "Mathematics"]},
            {"name": "Database Administrator", "skills": ["SQL", "MySQL", "PostgreSQL", "Database Design", "Performance Tuning", "Backup & Recovery"]}
        ]
    },
    {
        "branch": "Information Technology",
        "roles": [
            {"name": "Cloud Architect", "skills": ["AWS", "Azure", "Cloud Security", "Networking", "Linux", "Python"]},
            {"name": "Systems Analyst", "skills": ["Requirements Gathering", "UML", "SQL", "Business Analysis", "Communication"]},
            {"name": "IT Support Engineer", "skills": ["Troubleshooting", "Windows Server", "Linux", "Networking", "Hardware Maintenance"]},
            {"name": "Network Administrator", "skills": ["Routing", "Switching", "Firewalls", "VPN", "Cisco IOS"]}
        ]
    },
    {
        "branch": "Electronics and Communication Engineering",
        "roles": [
            {"name": "VLSI Design Engineer", "skills": ["Verilog", "VHDL", "Digital Logic", "ASIC Design", "FPGA"]},
            {"name": "RF Engineer", "skills": ["Electromagnetics", "RF Circuit Design", "Antenna Design", "MATLAB", "Wireless Communication"]},
            {"name": "Telecommunications Engineer", "skills": ["Signal Processing", "Networking", "Optical Communication", "Microwave Engineering"]},
            {"name": "Hardware Design Engineer", "skills": ["PCB Design", "Altium", "Eagle", "Analog Circuits", "Soldering"]}
        ]
    },
    {
        "branch": "Mechanical Engineering",
        "roles": [
            {"name": "Automotive Engineer", "skills": ["Vehicle Dynamics", "IC Engines", "AutoCAD", "MATLAB", "Thermodynamics"]},
            {"name": "Robotics Engineer", "skills": ["Kinematics", "C++", "Python", "Control Systems", "Machine Design", "Sensors"]},
            {"name": "HVAC Engineer", "skills": ["Heat Transfer", "Fluid Mechanics", "HVAC Design", "AutoCAD MEP", "Thermodynamics"]},
            {"name": "Aerospace Engineer", "skills": ["Aerodynamics", "Propulsion", "Flight Mechanics", "MATLAB", "CATIA"]}
        ]
    },
    {
        "branch": "Civil Engineering",
        "roles": [
            {"name": "Transportation Engineer", "skills": ["Traffic Engineering", "Highway Design", "AutoCAD Civil 3D", "Pavement Design"]},
            {"name": "Environmental Engineer", "skills": ["Water Treatment", "Waste Management", "Environmental Impact Assessment", "AutoCAD"]},
            {"name": "Urban Planner", "skills": ["GIS", "AutoCAD", "Urban Economics", "Zoning Laws", "Sustainability"]},
            {"name": "Geotechnical Engineer", "skills": ["Soil Mechanics", "Foundation Engineering", "GeoStudio", "Site Investigation"]}
        ]
    }
]

def seed():
    for branch_data in data:
        branch, _ = Branch.objects.get_or_create(name=branch_data["branch"])
        for role_data in branch_data["roles"]:
            job_role, _ = JobRole.objects.get_or_create(name=role_data["name"], branch=branch)
            for skill_name in role_data["skills"]:
                skill, _ = Skill.objects.get_or_create(name=skill_name)
                RequiredSkill.objects.get_or_create(job_role=job_role, skill=skill)

if __name__ == '__main__':
    seed()
    print("Database seeded successfully with ADDITIONAL Job Roles and Skills!")
