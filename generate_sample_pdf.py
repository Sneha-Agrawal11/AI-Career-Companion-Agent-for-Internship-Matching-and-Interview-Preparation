"""
Script to generate a sample resume PDF for testing.
"""
from fpdf import FPDF


class ResumePDF(FPDF):
    def header(self):
        self.set_font("Arial", "B", 16)
        self.cell(0, 10, "JOHN DOE", align="C", new_x="LMARGIN", new_y="NEXT")
        self.set_font("Arial", "I", 10)
        self.cell(0, 6, "john.doe@email.com | +1 (555) 123-4567 | linkedin.com/in/johndoe", align="C", new_x="LMARGIN", new_y="NEXT")
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(5)

    def section_title(self, title):
        self.set_font("Arial", "B", 12)
        self.set_text_color(0, 102, 204)
        self.cell(0, 8, title, new_x="LMARGIN", new_y="NEXT")
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(2)

    def section_body(self, text):
        self.set_font("Arial", "", 10)
        self.set_text_color(0, 0, 0)
        self.multi_cell(0, 5, text)
        self.ln(2)


pdf = ResumePDF()
pdf.add_page()

# Summary
pdf.section_title("PROFESSIONAL SUMMARY")
pdf.section_body(
    "Experienced software engineer with 5+ years of expertise in full-stack development, "
    "cloud architecture, and machine learning. Passionate about building scalable applications "
    "and leading cross-functional teams to deliver high-impact solutions."
)

# Skills
pdf.section_title("TECHNICAL SKILLS")
pdf.section_body(
    "Languages: Python, JavaScript, TypeScript, Java, SQL\n"
    "Frameworks: React, Node.js, Django, Flask, Spring Boot\n"
    "Cloud & DevOps: AWS (EC2, S3, Lambda), Docker, Kubernetes, Terraform, Jenkins\n"
    "Databases: PostgreSQL, MongoDB, Redis, Elasticsearch\n"
    "Tools: Git, Jira, Confluence, Figma, Postman"
)

# Experience
pdf.section_title("WORK EXPERIENCE")

pdf.set_font("Arial", "B", 10)
pdf.cell(0, 5, "Senior Software Engineer", new_x="LMARGIN", new_y="NEXT")
pdf.set_font("Arial", "I", 9)
pdf.cell(0, 5, "Tech Corp Inc. | Jan 2021 - Present", new_x="LMARGIN", new_y="NEXT")
pdf.set_font("Arial", "", 10)
pdf.section_body(
    "- Led a team of 5 engineers to build a microservices-based e-commerce platform\n"
    "- Designed and implemented RESTful APIs serving 1M+ daily requests\n"
    "- Reduced deployment time by 60% through CI/CD pipeline optimization\n"
    "- Migrated legacy monolith to cloud-native architecture on AWS"
)

pdf.set_font("Arial", "B", 10)
pdf.cell(0, 5, "Software Engineer", new_x="LMARGIN", new_y="NEXT")
pdf.set_font("Arial", "I", 9)
pdf.cell(0, 5, "StartupXYZ | Jun 2018 - Dec 2020", new_x="LMARGIN", new_y="NEXT")
pdf.set_font("Arial", "", 10)
pdf.section_body(
    "- Developed real-time data processing pipeline processing 10TB+ monthly\n"
    "- Built ML-powered recommendation system improving user engagement by 35%\n"
    "- Implemented automated testing framework achieving 95% code coverage"
)

# Education
pdf.section_title("EDUCATION")

pdf.set_font("Arial", "B", 10)
pdf.cell(0, 5, "Master of Science in Computer Science", new_x="LMARGIN", new_y="NEXT")
pdf.set_font("Arial", "", 10)
pdf.cell(0, 5, "Stanford University | 2016 - 2018 | GPA: 3.9/4.0", new_x="LMARGIN", new_y="NEXT")
pdf.ln(2)

pdf.set_font("Arial", "B", 10)
pdf.cell(0, 5, "Bachelor of Technology in Computer Engineering", new_x="LMARGIN", new_y="NEXT")
pdf.set_font("Arial", "", 10)
pdf.cell(0, 5, "MIT | 2012 - 2016 | GPA: 3.8/4.0", new_x="LMARGIN", new_y="NEXT")
pdf.ln(4)

# Certifications
pdf.section_title("CERTIFICATIONS")
pdf.section_body(
    "- AWS Certified Solutions Architect (2023)\n"
    "- Google Professional Cloud Architect (2022)\n"
    "- Certified Kubernetes Administrator (2022)\n"
    "- Scrum Master Certification (2021)"
)

# Projects
pdf.section_title("NOTABLE PROJECTS")
pdf.section_body(
    "Open-Source Contribution: Core contributor to Apache Spark - optimized shuffle operations (Python/Scala)\n"
    "Personal Project: Built an AI-powered code review tool using GPT-4 and React (github.com/johndoe/codereview)"
)

pdf.output("resume.pdf")
print("Sample resume.pdf generated successfully!")

