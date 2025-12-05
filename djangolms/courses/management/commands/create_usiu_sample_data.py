"""
Management command to create comprehensive sample data for USIU-A School of Science.
Run with: python manage.py create_usiu_sample_data
"""
import random
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from djangolms.accounts.models import User
from djangolms.courses.models import Course, Module, Material, Enrollment
from djangolms.assignments.models import (
    Assignment, Quiz, Question, QuestionChoice,
    Submission, QuizAttempt, QuizResponse
)
from djangolms.grades.models import GradeScale, GradeCategory, CourseGrade
from djangolms.notifications.models import Notification, Announcement


class Command(BaseCommand):
    help = 'Creates comprehensive sample data for USIU-A School of Science with Kenyan names'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing sample data before creating new data',
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('=' * 70))
        self.stdout.write(self.style.SUCCESS('Creating USIU-A School of Science Sample Data'))
        self.stdout.write(self.style.SUCCESS('=' * 70))

        if options['clear']:
            self._clear_existing_data()

        # Create instructors
        instructors = self._create_instructors()

        # Create students
        students = self._create_students()

        # Create courses
        courses = self._create_courses(instructors)

        # Enroll students in courses
        self._enroll_students(courses, students)

        # Create course content
        for course in courses:
            self._create_course_content(course)

        # Create grade scales and categories
        self._create_grade_structure(courses)

        # Generate student submissions and quiz attempts
        self.stdout.write('\n📝 Generating student submissions and quiz attempts...')
        submission_count, quiz_attempt_count = self._generate_submissions_and_attempts(courses, students)

        # Calculate grades
        self.stdout.write('\n📊 Calculating course grades...')
        grade_count = self._calculate_all_grades()

        # Create announcements and notifications
        self.stdout.write('\n📢 Creating announcements and notifications...')
        announcement_count, notification_count = self._create_notifications(courses, students)

        self.stdout.write(self.style.SUCCESS('\n' + '=' * 70))
        self.stdout.write(self.style.SUCCESS('✓ Sample data created successfully!'))
        self.stdout.write(self.style.SUCCESS('=' * 70))
        self.stdout.write(self.style.SUCCESS(f'\n📊 Summary:'))
        self.stdout.write(f'   • {len(instructors)} Instructors created')
        self.stdout.write(f'   • {len(students)} Students created')
        self.stdout.write(f'   • {len(courses)} Courses created')
        self.stdout.write(f'   • Course enrollments completed')
        self.stdout.write(f'   • Course content (modules, materials, assignments, quizzes) added')
        self.stdout.write(f'   • {submission_count} Assignment submissions created')
        self.stdout.write(f'   • {quiz_attempt_count} Quiz attempts completed')
        self.stdout.write(f'   • {grade_count} Course grades calculated')
        self.stdout.write(f'   • {announcement_count} Course announcements posted')
        self.stdout.write(f'   • {notification_count} Student notifications sent')

        self.stdout.write(self.style.SUCCESS('\n📚 Login Credentials:'))
        self.stdout.write('   Instructors: username = first_name.last_name (lowercase), password = instructor123')
        self.stdout.write('   Students: username = first_name.last_name (lowercase), password = student123')
        self.stdout.write('   Example: username=james.kamau, password=student123')

        self.stdout.write(self.style.SUCCESS('\n🎓 View the gradebook to see calculated grades for all students!'))

    def _clear_existing_data(self):
        """Clear existing sample data."""
        self.stdout.write(self.style.WARNING('\n⚠ Clearing existing data...'))

        # Clear notifications and announcements
        Notification.objects.all().delete()
        Announcement.objects.all().delete()

        # Clear grades
        CourseGrade.objects.all().delete()
        GradeCategory.objects.all().delete()
        GradeScale.objects.all().delete()

        # Clear quiz attempts and submissions
        QuizResponse.objects.all().delete()
        QuizAttempt.objects.all().delete()
        Submission.objects.all().delete()

        # Clear enrollments
        Enrollment.objects.all().delete()

        # Clear course content
        Material.objects.all().delete()
        Module.objects.all().delete()
        QuestionChoice.objects.all().delete()
        Question.objects.all().delete()
        Quiz.objects.all().delete()
        Assignment.objects.all().delete()

        # Clear courses (keep admin courses)
        Course.objects.exclude(instructor__username='admin').delete()

        # Clear users (keep superusers)
        User.objects.filter(is_superuser=False).delete()

        self.stdout.write(self.style.SUCCESS('✓ Existing data cleared'))

    def _create_instructors(self):
        """Create 10 instructors with Kenyan names."""
        self.stdout.write('\n📝 Creating instructors...')

        instructors_data = [
            {'first_name': 'James', 'last_name': 'Kamau', 'email': 'james.kamau@usiu.ac.ke', 'dept': 'Computer Science'},
            {'first_name': 'Grace', 'last_name': 'Wanjiru', 'email': 'grace.wanjiru@usiu.ac.ke', 'dept': 'Mathematics'},
            {'first_name': 'David', 'last_name': 'Ochieng', 'email': 'david.ochieng@usiu.ac.ke', 'dept': 'Physics'},
            {'first_name': 'Mary', 'last_name': 'Akinyi', 'email': 'mary.akinyi@usiu.ac.ke', 'dept': 'Chemistry'},
            {'first_name': 'Peter', 'last_name': 'Mwangi', 'email': 'peter.mwangi@usiu.ac.ke', 'dept': 'Biology'},
            {'first_name': 'Sarah', 'last_name': 'Njeri', 'email': 'sarah.njeri@usiu.ac.ke', 'dept': 'Statistics'},
            {'first_name': 'John', 'last_name': 'Otieno', 'email': 'john.otieno@usiu.ac.ke', 'dept': 'Computer Science'},
            {'first_name': 'Ruth', 'last_name': 'Wangari', 'email': 'ruth.wangari@usiu.ac.ke', 'dept': 'Mathematics'},
            {'first_name': 'Daniel', 'last_name': 'Kipchoge', 'email': 'daniel.kipchoge@usiu.ac.ke', 'dept': 'Environmental Science'},
            {'first_name': 'Lucy', 'last_name': 'Mutua', 'email': 'lucy.mutua@usiu.ac.ke', 'dept': 'Information Systems'},
        ]

        instructors = []
        for data in instructors_data:
            username = f"{data['first_name'].lower()}.{data['last_name'].lower()}"
            instructor, created = User.objects.get_or_create(
                username=username,
                defaults={
                    'email': data['email'],
                    'first_name': data['first_name'],
                    'last_name': data['last_name'],
                    'role': User.Role.INSTRUCTOR,
                    'is_active': True,
                }
            )
            if created:
                instructor.set_password('instructor123')
                instructor.save()
                self.stdout.write(f'  ✓ Created: Dr. {data["first_name"]} {data["last_name"]} ({data["dept"]})')
            instructors.append(instructor)

        return instructors

    def _create_students(self):
        """Create 50 students with Kenyan names."""
        self.stdout.write('\n📝 Creating students...')

        students_data = [
            {'first_name': 'Brian', 'last_name': 'Kimani'},
            {'first_name': 'Faith', 'last_name': 'Chebet'},
            {'first_name': 'Kevin', 'last_name': 'Omondi'},
            {'first_name': 'Nancy', 'last_name': 'Wambui'},
            {'first_name': 'Emmanuel', 'last_name': 'Kiprop'},
            {'first_name': 'Mercy', 'last_name': 'Nyambura'},
            {'first_name': 'Dennis', 'last_name': 'Muema'},
            {'first_name': 'Alice', 'last_name': 'Jebet'},
            {'first_name': 'Vincent', 'last_name': 'Karanja'},
            {'first_name': 'Christine', 'last_name': 'Wairimu'},
            {'first_name': 'Michael', 'last_name': 'Wekesa'},
            {'first_name': 'Joan', 'last_name': 'Moraa'},
            {'first_name': 'Patrick', 'last_name': 'Kiptoo'},
            {'first_name': 'Susan', 'last_name': 'Adhiambo'},
            {'first_name': 'Timothy', 'last_name': 'Njoroge'},
            {'first_name': 'Catherine', 'last_name': 'Mumbi'},
            {'first_name': 'Samuel', 'last_name': 'Kibet'},
            {'first_name': 'Esther', 'last_name': 'Wanjiku'},
            {'first_name': 'George', 'last_name': 'Okoth'},
            {'first_name': 'Diana', 'last_name': 'Chemutai'},
            {'first_name': 'Stephen', 'last_name': 'Njenga'},
            {'first_name': 'Josephine', 'last_name': 'Nafula'},
            {'first_name': 'Martin', 'last_name': 'Kariuki'},
            {'first_name': 'Lydia', 'last_name': 'Jepkemoi'},
            {'first_name': 'Anthony', 'last_name': 'Musyoka'},
            {'first_name': 'Rachel', 'last_name': 'Wangui'},
            {'first_name': 'Philip', 'last_name': 'Koech'},
            {'first_name': 'Caroline', 'last_name': 'Njoki'},
            {'first_name': 'Joseph', 'last_name': 'Omolo'},
            {'first_name': 'Betty', 'last_name': 'Chepkemoi'},
            {'first_name': 'Edwin', 'last_name': 'Mutiso'},
            {'first_name': 'Agnes', 'last_name': 'Nyawira'},
            {'first_name': 'Robert', 'last_name': 'Kemboi'},
            {'first_name': 'Jane', 'last_name': 'Achieng'},
            {'first_name': 'Francis', 'last_name': 'Githinji'},
            {'first_name': 'Monica', 'last_name': 'Chelangat'},
            {'first_name': 'Collins', 'last_name': 'Ouma'},
            {'first_name': 'Beatrice', 'last_name': 'Wanjiru'},
            {'first_name': 'Alex', 'last_name': 'Kiplagat'},
            {'first_name': 'Margaret', 'last_name': 'Muthoni'},
            {'first_name': 'Nicholas', 'last_name': 'Odongo'},
            {'first_name': 'Elizabeth', 'last_name': 'Cheptoo'},
            {'first_name': 'Kenneth', 'last_name': 'Mburu'},
            {'first_name': 'Anne', 'last_name': 'Awino'},
            {'first_name': 'Jackson', 'last_name': 'Kiprono'},
            {'first_name': 'Victoria', 'last_name': 'Wangeci'},
            {'first_name': 'Paul', 'last_name': 'Owino'},
            {'first_name': 'Stella', 'last_name': 'Jepchirchir'},
            {'first_name': 'Lawrence', 'last_name': 'Maina'},
            {'first_name': 'Pauline', 'last_name': 'Atieno'},
        ]

        students = []
        for i, data in enumerate(students_data, 1):
            username = f"{data['first_name'].lower()}.{data['last_name'].lower()}"
            email = f"{username}@student.usiu.ac.ke"

            student, created = User.objects.get_or_create(
                username=username,
                defaults={
                    'email': email,
                    'first_name': data['first_name'],
                    'last_name': data['last_name'],
                    'role': User.Role.STUDENT,
                    'is_active': True,
                }
            )
            if created:
                student.set_password('student123')
                student.save()
                if i % 10 == 0:
                    self.stdout.write(f'  ✓ Created {i} students...')
            students.append(student)

        self.stdout.write(f'  ✓ Total: {len(students)} students created')
        return students

    def _create_courses(self, instructors):
        """Create 20 courses for USIU-A School of Science."""
        self.stdout.write('\n📝 Creating courses...')

        courses_data = [
            # Computer Science (4 courses)
            {
                'code': 'CS101',
                'title': 'Introduction to Programming',
                'description': 'Learn programming fundamentals using Python. Covers variables, control structures, functions, and basic data structures.',
                'instructor_idx': 0,
                'credits': 3,
            },
            {
                'code': 'CS201',
                'title': 'Data Structures and Algorithms',
                'description': 'Study fundamental data structures (arrays, linked lists, trees, graphs) and algorithms for searching, sorting, and optimization.',
                'instructor_idx': 0,
                'credits': 4,
            },
            {
                'code': 'CS301',
                'title': 'Database Management Systems',
                'description': 'Learn database design, SQL, normalization, and transaction management. Includes hands-on projects with PostgreSQL.',
                'instructor_idx': 6,
                'credits': 3,
            },
            {
                'code': 'CS401',
                'title': 'Web Application Development',
                'description': 'Build modern web applications using Django, React, and REST APIs. Includes deployment and security best practices.',
                'instructor_idx': 6,
                'credits': 4,
            },
            # Mathematics (4 courses)
            {
                'code': 'MATH101',
                'title': 'Calculus I',
                'description': 'Introduction to differential and integral calculus. Covers limits, derivatives, and applications.',
                'instructor_idx': 1,
                'credits': 4,
            },
            {
                'code': 'MATH201',
                'title': 'Linear Algebra',
                'description': 'Study vector spaces, matrices, determinants, eigenvalues, and linear transformations.',
                'instructor_idx': 1,
                'credits': 3,
            },
            {
                'code': 'MATH301',
                'title': 'Probability and Statistics',
                'description': 'Introduction to probability theory, random variables, distributions, and statistical inference.',
                'instructor_idx': 7,
                'credits': 3,
            },
            {
                'code': 'MATH401',
                'title': 'Differential Equations',
                'description': 'Study ordinary and partial differential equations with applications in science and engineering.',
                'instructor_idx': 7,
                'credits': 4,
            },
            # Physics (3 courses)
            {
                'code': 'PHYS101',
                'title': 'General Physics I',
                'description': 'Introduction to mechanics, waves, and thermodynamics. Includes laboratory component.',
                'instructor_idx': 2,
                'credits': 4,
            },
            {
                'code': 'PHYS201',
                'title': 'Electricity and Magnetism',
                'description': 'Study electric fields, circuits, magnetic fields, and electromagnetic induction.',
                'instructor_idx': 2,
                'credits': 4,
            },
            {
                'code': 'PHYS301',
                'title': 'Modern Physics',
                'description': 'Introduction to quantum mechanics, relativity, atomic and nuclear physics.',
                'instructor_idx': 2,
                'credits': 3,
            },
            # Chemistry (3 courses)
            {
                'code': 'CHEM101',
                'title': 'General Chemistry',
                'description': 'Introduction to chemical principles including atomic structure, bonding, and reactions.',
                'instructor_idx': 3,
                'credits': 4,
            },
            {
                'code': 'CHEM201',
                'title': 'Organic Chemistry',
                'description': 'Study of carbon compounds, reaction mechanisms, and synthesis of organic molecules.',
                'instructor_idx': 3,
                'credits': 4,
            },
            {
                'code': 'CHEM301',
                'title': 'Analytical Chemistry',
                'description': 'Learn analytical techniques including chromatography, spectroscopy, and electrochemistry.',
                'instructor_idx': 3,
                'credits': 3,
            },
            # Biology (3 courses)
            {
                'code': 'BIO101',
                'title': 'Introduction to Biology',
                'description': 'Study cells, genetics, evolution, and ecology. Includes laboratory work.',
                'instructor_idx': 4,
                'credits': 4,
            },
            {
                'code': 'BIO201',
                'title': 'Molecular Biology',
                'description': 'Study DNA, RNA, protein synthesis, and gene regulation at the molecular level.',
                'instructor_idx': 4,
                'credits': 3,
            },
            {
                'code': 'BIO301',
                'title': 'Microbiology',
                'description': 'Study bacteria, viruses, fungi, and their roles in health, disease, and environment.',
                'instructor_idx': 4,
                'credits': 3,
            },
            # Statistics & Data Science (2 courses)
            {
                'code': 'STAT201',
                'title': 'Statistical Methods',
                'description': 'Applied statistics including hypothesis testing, regression, and ANOVA using R.',
                'instructor_idx': 5,
                'credits': 3,
            },
            {
                'code': 'DATA301',
                'title': 'Introduction to Data Science',
                'description': 'Learn data analysis, visualization, and machine learning using Python and scikit-learn.',
                'instructor_idx': 5,
                'credits': 4,
            },
            # Environmental Science (1 course)
            {
                'code': 'ENV201',
                'title': 'Environmental Science',
                'description': 'Study ecosystems, climate change, pollution, and sustainable development in Kenya and globally.',
                'instructor_idx': 8,
                'credits': 3,
            },
        ]

        courses = []
        for data in courses_data:
            instructor = instructors[data['instructor_idx']]

            course, created = Course.objects.get_or_create(
                code=data['code'],
                defaults={
                    'title': data['title'],
                    'description': data['description'],
                    'instructor': instructor,
                    'status': Course.Status.PUBLISHED,
                    'max_students': random.randint(30, 60),
                    'start_date': timezone.now().date(),
                    'end_date': (timezone.now() + timedelta(days=120)).date(),
                }
            )

            if created:
                self.stdout.write(f'  ✓ Created: {data["code"]} - {data["title"]}')
            courses.append(course)

        return courses

    def _enroll_students(self, courses, students):
        """Enroll students in courses randomly."""
        self.stdout.write('\n📝 Enrolling students in courses...')

        enrollments_created = 0
        for student in students:
            # Each student enrolls in 4-6 random courses
            num_courses = random.randint(4, 6)
            selected_courses = random.sample(courses, num_courses)

            for course in selected_courses:
                enrollment, created = Enrollment.objects.get_or_create(
                    student=student,
                    course=course,
                    defaults={
                        'status': 'ENROLLED',
                        'enrolled_at': timezone.now(),
                    }
                )
                if created:
                    enrollments_created += 1

        self.stdout.write(f'  ✓ Created {enrollments_created} course enrollments')

    def _create_course_content(self, course):
        """Create modules, materials, assignments, and quizzes for a course."""

        # Create 4-6 modules
        num_modules = random.randint(4, 6)

        # Track whether we've created project and exam assignments
        project_created = False
        exam_created = False

        for i in range(1, num_modules + 1):
            module = Module.objects.create(
                course=course,
                title=f'Module {i}: {self._get_module_title(course.code, i)}',
                description=f'Learning objectives and content for module {i}',
                order=i,
            )

            # Create 2-4 materials per module
            num_materials = random.randint(2, 4)
            for j in range(1, num_materials + 1):
                Material.objects.create(
                    module=module,
                    title=f'{self._get_material_title(course.code, i, j)}',
                    content=self._get_material_content(course.code, i, j),
                    material_type=random.choice(['LECTURE', 'READING', 'VIDEO', 'LAB']),
                    order=j,
                )

            # Create 1 assignment per module (homework type)
            Assignment.objects.create(
                course=course,
                title=f'{course.code} - Module {i} Assignment',
                description=self._get_assignment_description(course.code, i),
                assignment_type='HOMEWORK',
                due_date=timezone.now() + timedelta(days=i*10),
                total_points=100,
            )

            # Create 1 quiz assignment per module
            quiz_assignment = Assignment.objects.create(
                course=course,
                title=f'{course.code} - Module {i} Quiz',
                description=f'Assessment quiz for module {i} content',
                assignment_type='QUIZ',
                due_date=timezone.now() + timedelta(days=i*10 + 5),
                total_points=100,
            )

            # Create Quiz linked to the assignment
            quiz = Quiz.objects.create(
                assignment=quiz_assignment,
                time_limit=30,  # 30 minutes
                allow_multiple_attempts=True,
                max_attempts=2,
                show_correct_answers=True,
                randomize_questions=True,
            )

            # Create 5-8 questions per quiz
            num_questions = random.randint(5, 8)
            for q in range(1, num_questions + 1):
                question = Question.objects.create(
                    quiz=quiz,
                    text=self._get_question_text(course.code, i, q),
                    question_type='MULTIPLE_CHOICE',
                    points=10,
                    order=q,
                )

                # Create 4 choices (1 correct, 3 incorrect)
                choices_data = self._get_question_choices(course.code, i, q)
                for choice_idx, (choice_text, is_correct) in enumerate(choices_data):
                    QuestionChoice.objects.create(
                        question=question,
                        text=choice_text,
                        is_correct=is_correct,
                        order=choice_idx + 1,
                    )

            # Add a project assignment in the middle of the course
            if not project_created and i == num_modules // 2:
                Assignment.objects.create(
                    course=course,
                    title=f'{course.code} - Course Project',
                    description=f'Complete a comprehensive project that demonstrates your understanding of {course.title} concepts covered so far.',
                    assignment_type='PROJECT',
                    due_date=timezone.now() + timedelta(days=i*10 + 15),
                    total_points=150,
                )
                project_created = True

            # Add a final exam assignment in the last module
            if not exam_created and i == num_modules:
                Assignment.objects.create(
                    course=course,
                    title=f'{course.code} - Final Exam',
                    description=f'Comprehensive final exam covering all course material for {course.title}.',
                    assignment_type='EXAM',
                    due_date=timezone.now() + timedelta(days=i*10 + 20),
                    total_points=200,
                )
                exam_created = True

    def _get_module_title(self, course_code, module_num):
        """Generate module title based on course."""
        titles = {
            'CS101': ['Python Basics', 'Control Structures', 'Functions', 'Data Structures', 'File Handling', 'OOP Concepts'],
            'CS201': ['Arrays & Lists', 'Stacks & Queues', 'Trees', 'Graphs', 'Sorting Algorithms', 'Dynamic Programming'],
            'MATH101': ['Limits', 'Derivatives', 'Applications of Derivatives', 'Integrals', 'Applications of Integrals'],
            'PHYS101': ['Kinematics', 'Newton\'s Laws', 'Energy & Work', 'Waves', 'Thermodynamics'],
            'CHEM101': ['Atomic Structure', 'Chemical Bonding', 'Stoichiometry', 'Chemical Reactions', 'Solutions'],
            'BIO101': ['Cell Biology', 'Genetics', 'Evolution', 'Ecology', 'Human Biology'],
        }

        if course_code in titles and module_num <= len(titles[course_code]):
            return titles[course_code][module_num - 1]
        return f'Core Concepts Part {module_num}'

    def _get_material_title(self, course_code, module_num, material_num):
        """Generate material title."""
        prefixes = ['Lecture Notes:', 'Lab Exercise:', 'Reading:', 'Video Tutorial:', 'Case Study:']
        return f'{random.choice(prefixes)} Topic {module_num}.{material_num}'

    def _get_material_content(self, course_code, module_num, material_num):
        """Generate material content."""
        return f"""
# {self._get_material_title(course_code, module_num, material_num)}

## Learning Objectives
By the end of this material, you should be able to:
- Understand the key concepts covered in this section
- Apply these concepts to solve problems
- Demonstrate proficiency in practical applications

## Content
This material covers important topics related to {course_code} Module {module_num}.
Students are expected to review all materials and complete associated exercises.

## Resources
- Textbook chapters related to this topic
- Online resources and tutorials
- Practice problems and examples

## Next Steps
1. Review the material thoroughly
2. Complete the practice exercises
3. Prepare for the module quiz
4. Submit the module assignment on time
"""

    def _get_assignment_description(self, course_code, module_num):
        """Generate assignment description."""
        return f"""
## {course_code} Module {module_num} Assignment

### Instructions
Complete the following tasks and submit your work by the due date.

### Requirements
1. Answer all questions thoroughly
2. Show your work and methodology
3. Submit in PDF or DOCX format
4. Include your name and student ID

### Grading Criteria
- Completeness (40%)
- Accuracy (40%)
- Presentation (20%)

### Submission Guidelines
Upload your completed assignment through the course portal. Late submissions will be penalized according to the course policy.
"""

    def _get_question_text(self, course_code, module_num, question_num):
        """Generate question text based on course."""
        questions = {
            'CS': [
                'What is the time complexity of binary search?',
                'Which data structure uses LIFO principle?',
                'What is the purpose of a constructor in OOP?',
                'Which sorting algorithm has O(n log n) average case?',
                'What does SQL stand for?',
                'What is the difference between a list and a tuple in Python?',
                'What is recursion?',
                'What is the purpose of the break statement?',
            ],
            'MATH': [
                'What is the derivative of sin(x)?',
                'What is the integral of 2x?',
                'What is the determinant of a 2x2 identity matrix?',
                'What is the Pythagorean theorem?',
                'What is a prime number?',
                'What is the slope-intercept form of a line?',
                'What is a vector?',
                'What is probability?',
            ],
            'PHYS': [
                'What is Newton\'s first law?',
                'What is the speed of light in vacuum?',
                'What is the unit of force?',
                'What is kinetic energy?',
                'What is Ohm\'s law?',
                'What is a wave?',
                'What is temperature?',
                'What is electromagnetic radiation?',
            ],
            'CHEM': [
                'What is an atom?',
                'What is a covalent bond?',
                'What is the pH scale?',
                'What is oxidation?',
                'What is a catalyst?',
                'What is molarity?',
                'What is an isotope?',
                'What is a chemical equation?',
            ],
            'BIO': [
                'What is DNA?',
                'What is photosynthesis?',
                'What is a cell?',
                'What is mitosis?',
                'What is natural selection?',
                'What is an ecosystem?',
                'What is a gene?',
                'What is cellular respiration?',
            ],
        }

        prefix = course_code[:2] if course_code[:2] in ['CS'] else course_code[:4]
        if prefix in questions:
            return random.choice(questions[prefix])
        return f'Question {question_num}: What is the key concept in this module?'

    def _get_question_choices(self, course_code, module_num, question_num):
        """Generate question choices (correct answer + 3 distractors)."""
        # Return list of (choice_text, is_correct) tuples
        choices = [
            ('O(log n)', True),
            ('O(n)', False),
            ('O(n²)', False),
            ('O(1)', False),
        ]
        random.shuffle(choices)
        return choices

    def _create_grade_structure(self, courses):
        """Create grade scales and categories for all courses."""
        self.stdout.write('\n📊 Setting up grade scales and categories...')

        for course in courses:
            # Create grade scale
            GradeScale.objects.get_or_create(
                course=course,
                defaults={
                    'a_min': 90.00,
                    'b_min': 80.00,
                    'c_min': 70.00,
                    'd_min': 60.00,
                    'use_plus_minus': True,
                }
            )

            # Create grade categories with weights
            categories = [
                {'name': 'Homework', 'weight': 20.00, 'assignment_type': 'HOMEWORK', 'drop_lowest': 1},
                {'name': 'Quizzes', 'weight': 30.00, 'assignment_type': 'QUIZ', 'drop_lowest': 0},
                {'name': 'Projects', 'weight': 25.00, 'assignment_type': 'PROJECT', 'drop_lowest': 0},
                {'name': 'Exams', 'weight': 25.00, 'assignment_type': 'EXAM', 'drop_lowest': 0},
            ]

            for cat_data in categories:
                GradeCategory.objects.get_or_create(
                    course=course,
                    assignment_type=cat_data['assignment_type'],
                    defaults={
                        'name': cat_data['name'],
                        'weight': cat_data['weight'],
                        'drop_lowest': cat_data['drop_lowest'],
                    }
                )

        self.stdout.write(f'  ✓ Grade scales and categories configured for {len(courses)} courses')

    def _generate_submissions_and_attempts(self, courses, students):
        """Generate assignment submissions and quiz attempts for students."""
        submission_count = 0
        quiz_attempt_count = 0

        for course in courses:
            # Get enrolled students
            enrollments = Enrollment.objects.filter(course=course, status='ENROLLED')
            enrolled_students = [e.student for e in enrollments]

            if not enrolled_students:
                continue

            # Get all assignments (non-quiz)
            assignments = Assignment.objects.filter(course=course).exclude(assignment_type='QUIZ')

            for assignment in assignments:
                # 70-90% of students submit assignments
                num_submissions = int(len(enrolled_students) * random.uniform(0.7, 0.9))
                submitting_students = random.sample(enrolled_students, num_submissions)

                for student in submitting_students:
                    # Create submission
                    submission = Submission.objects.create(
                        assignment=assignment,
                        student=student,
                        submission_text=f"Submission for {assignment.title} by {student.get_full_name()}.\n\nThis is my completed assignment work.",
                        submitted_at=timezone.now() - timedelta(days=random.randint(0, 30)),
                        graded=True,
                        score=random.randint(60, 100),  # Random score between 60-100
                        feedback=random.choice([
                            "Good work! Well done.",
                            "Excellent submission. Keep it up!",
                            "Nice effort. Could improve on clarity.",
                            "Great job! Very thorough.",
                            "Good understanding of the concepts.",
                        ]),
                        graded_by=course.instructor,
                        graded_at=timezone.now() - timedelta(days=random.randint(0, 15)),
                    )
                    submission_count += 1

            # Get all quizzes
            quizzes = Quiz.objects.filter(assignment__course=course)

            for quiz in quizzes:
                # 75-95% of students attempt quizzes
                num_attempts = int(len(enrolled_students) * random.uniform(0.75, 0.95))
                attempting_students = random.sample(enrolled_students, num_attempts)

                for student in attempting_students:
                    # Create quiz attempt
                    attempt = QuizAttempt.objects.create(
                        quiz=quiz,
                        student=student,
                        attempt_number=1,
                        started_at=timezone.now() - timedelta(days=random.randint(0, 30)),
                    )

                    # Create responses for each question
                    questions = Question.objects.filter(quiz=quiz)
                    for question in questions:
                        # Get all choices
                        choices = list(QuestionChoice.objects.filter(question=question))
                        if choices:
                            # 70-90% chance of getting the answer correct
                            if random.random() < 0.8:
                                # Pick correct answer
                                correct_choice = next((c for c in choices if c.is_correct), None)
                                answer = correct_choice.choice_text if correct_choice else choices[0].choice_text
                            else:
                                # Pick random answer
                                answer = random.choice(choices).choice_text

                            QuizResponse.objects.create(
                                attempt=attempt,
                                question=question,
                                answer_text=answer,
                            )

                    # Grade the quiz
                    attempt.grade_quiz()
                    quiz_attempt_count += 1

        return submission_count, quiz_attempt_count

    def _calculate_all_grades(self):
        """Calculate grades for all enrollments."""
        grade_count = 0

        enrollments = Enrollment.objects.filter(status='ENROLLED')

        for enrollment in enrollments:
            # Create or get course grade
            course_grade, created = CourseGrade.objects.get_or_create(
                enrollment=enrollment
            )

            # Calculate the grade
            course_grade.calculate_grade()
            grade_count += 1

        self.stdout.write(f'  ✓ Calculated grades for {grade_count} enrollments')
        return grade_count

    def _create_notifications(self, courses, students):
        """Create sample announcements and notifications."""
        announcement_count = 0
        notification_count = 0

        announcement_templates = [
            {
                'title': 'Welcome to {course_title}!',
                'content': 'Welcome to {course_title}! I\'m excited to have you in this course. Please review the syllabus and course materials. If you have any questions, feel free to reach out during office hours.',
                'priority': 'NORMAL',
            },
            {
                'title': 'Midterm Exam Schedule',
                'content': 'The midterm exam for {course_title} is scheduled for next week. Please review all materials from modules 1-3. The exam will be held during regular class time. Good luck!',
                'priority': 'HIGH',
            },
            {
                'title': 'Assignment Deadline Reminder',
                'content': 'Reminder: The assignment for Module 2 is due this Friday at 11:59 PM. Please submit your work through the course portal. Late submissions will incur a 10% penalty per day.',
                'priority': 'NORMAL',
            },
            {
                'title': 'Office Hours Update',
                'content': 'My office hours this week will be on Tuesday and Thursday from 2-4 PM. Feel free to drop by if you have questions about the course material or assignments.',
                'priority': 'LOW',
            },
        ]

        for course in courses:
            # Create 2-3 announcements per course
            num_announcements = random.randint(2, 3)
            selected_templates = random.sample(announcement_templates, min(num_announcements, len(announcement_templates)))

            for template in selected_templates:
                announcement = Announcement.objects.create(
                    course=course,
                    author=course.instructor,
                    title=template['title'].format(course_title=course.title),
                    content=template['content'].format(course_title=course.title),
                    priority=template['priority'],
                    pinned=random.choice([True, False]) if template['priority'] == 'HIGH' else False,
                    publish_at=timezone.now() - timedelta(days=random.randint(1, 20)),
                )
                announcement_count += 1

                # Create notifications for enrolled students
                enrollments = Enrollment.objects.filter(course=course, status='ENROLLED')[:10]  # Notify first 10 students
                for enrollment in enrollments:
                    Notification.objects.create(
                        recipient=enrollment.student,
                        notification_type='ANNOUNCEMENT',
                        title=f'New announcement in {course.code}',
                        message=template['title'].format(course_title=course.title),
                        related_course=course,
                        related_announcement=announcement,
                        action_url=f'/courses/{course.id}/announcements/',
                        is_read=random.choice([True, False]),
                    )
                    notification_count += 1

        # Create some grading notifications
        graded_submissions = Submission.objects.filter(graded=True)[:50]  # First 50 graded submissions
        for submission in graded_submissions:
            Notification.objects.create(
                recipient=submission.student,
                notification_type='GRADE',
                title=f'Assignment Graded: {submission.assignment.title}',
                message=f'Your assignment "{submission.assignment.title}" has been graded. Score: {submission.score}/{submission.assignment.total_points}',
                related_course=submission.assignment.course,
                action_url=f'/assignments/{submission.assignment.id}/submission/',
                is_read=random.choice([True, False]),
            )
            notification_count += 1

        self.stdout.write(f'  ✓ Created {announcement_count} announcements')
        self.stdout.write(f'  ✓ Sent {notification_count} notifications')

        return announcement_count, notification_count
