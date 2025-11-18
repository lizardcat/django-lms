"""
Management command to create sample quizzes, assignments, and course materials.
Run with: python manage.py create_sample_data
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from djangolms.accounts.models import User
from djangolms.courses.models import Course, Module, Material
from djangolms.assignments.models import Assignment, Quiz, Question, QuestionChoice


class Command(BaseCommand):
    help = 'Creates sample quizzes, assignments, and course materials for testing'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing sample data before creating new data',
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Creating sample data...'))

        # Get or create an instructor
        instructor = self._get_or_create_instructor()

        # Get or create courses
        courses = self._get_or_create_courses(instructor)

        # Create sample data for each course
        for course in courses:
            self.stdout.write(f'\nProcessing course: {course.code}')

            # Create modules and materials
            self._create_modules_and_materials(course, instructor)

            # Create assignments
            self._create_assignments(course)

            # Create quizzes
            self._create_quizzes(course)

        self.stdout.write(self.style.SUCCESS('\n✓ Sample data created successfully!'))
        self.stdout.write(self.style.SUCCESS('\nYou can now:'))
        self.stdout.write('  • View courses in Django admin')
        self.stdout.write('  • See modules and materials under Courses')
        self.stdout.write('  • Check quizzes under Assignments > Quiz')
        self.stdout.write('  • Review assignments under Assignments')

    def _get_or_create_instructor(self):
        """Get or create a sample instructor."""
        instructor, created = User.objects.get_or_create(
            username='prof_smith',
            defaults={
                'email': 'prof.smith@university.edu',
                'first_name': 'John',
                'last_name': 'Smith',
                'role': User.Role.INSTRUCTOR,
                'is_active': True,
            }
        )
        if created:
            instructor.set_password('instructor123')
            instructor.save()
            self.stdout.write(self.style.SUCCESS(f'✓ Created instructor: {instructor.username}'))
        else:
            self.stdout.write(f'  Using existing instructor: {instructor.username}')
        return instructor

    def _get_or_create_courses(self, instructor):
        """Get or create sample courses."""
        courses_data = [
            {
                'code': 'CS101',
                'title': 'Introduction to Computer Science',
                'description': 'Learn the fundamentals of programming and computer science.',
                'status': Course.Status.PUBLISHED,
            },
            {
                'code': 'WEB201',
                'title': 'Web Development Fundamentals',
                'description': 'Master HTML, CSS, JavaScript, and modern web frameworks.',
                'status': Course.Status.PUBLISHED,
            },
        ]

        courses = []
        for course_data in courses_data:
            course, created = Course.objects.get_or_create(
                code=course_data['code'],
                defaults={
                    **course_data,
                    'instructor': instructor,
                    'max_students': 50,
                    'start_date': timezone.now().date(),
                    'end_date': (timezone.now() + timedelta(days=120)).date(),
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'✓ Created course: {course.code}'))
            else:
                self.stdout.write(f'  Using existing course: {course.code}')
            courses.append(course)

        return courses

    def _create_modules_and_materials(self, course, instructor):
        """Create sample modules and materials for a course."""
        if course.code == 'CS101':
            modules_data = [
                {
                    'title': 'Week 1: Introduction to Programming',
                    'description': 'Learn the basics of programming and algorithms.',
                    'materials': [
                        {
                            'title': 'Course Syllabus',
                            'description': 'Overview of course objectives, schedule, and grading policy.',
                            'material_type': Material.MaterialType.DOCUMENT,
                            'url': 'https://example.com/syllabus.pdf',
                        },
                        {
                            'title': 'Introduction to Python - Video Lecture',
                            'description': 'Watch this 45-minute introduction to Python programming.',
                            'material_type': Material.MaterialType.VIDEO,
                            'url': 'https://www.youtube.com/watch?v=kqtD5dpn9C8',
                            'embed_code': '<iframe width="560" height="315" src="https://www.youtube.com/embed/kqtD5dpn9C8" frameborder="0" allowfullscreen></iframe>',
                            'is_required': True,
                        },
                        {
                            'title': 'Python Official Documentation',
                            'description': 'Reference documentation for Python 3.',
                            'material_type': Material.MaterialType.LINK,
                            'url': 'https://docs.python.org/3/',
                        },
                    ],
                },
                {
                    'title': 'Week 2: Variables and Data Types',
                    'description': 'Understanding variables, data types, and basic operations.',
                    'materials': [
                        {
                            'title': 'Variables and Data Types - Lecture Slides',
                            'description': 'Comprehensive slides covering Python data types.',
                            'material_type': Material.MaterialType.PRESENTATION,
                            'url': 'https://example.com/week2-slides.pdf',
                            'is_required': True,
                        },
                        {
                            'title': 'Python Type System Tutorial',
                            'description': 'Interactive tutorial on Python types.',
                            'material_type': Material.MaterialType.LINK,
                            'url': 'https://realpython.com/python-type-checking/',
                        },
                    ],
                },
                {
                    'title': 'Week 3: Control Flow',
                    'description': 'If statements, loops, and program flow control.',
                    'materials': [
                        {
                            'title': 'Control Flow - Video Lecture',
                            'description': 'Learn about if statements, for loops, and while loops.',
                            'material_type': Material.MaterialType.VIDEO,
                            'url': 'https://www.youtube.com/watch?v=HZARImviDxg',
                            'is_required': True,
                        },
                        {
                            'title': 'Practice Exercises',
                            'description': 'Download and complete these practice problems.',
                            'material_type': Material.MaterialType.FILE,
                            'url': 'https://example.com/exercises.pdf',
                        },
                    ],
                },
            ]
        else:  # WEB201
            modules_data = [
                {
                    'title': 'Module 1: HTML Fundamentals',
                    'description': 'Learn HTML structure, tags, and semantic markup.',
                    'materials': [
                        {
                            'title': 'HTML Basics - MDN Guide',
                            'description': 'Comprehensive guide to HTML from Mozilla.',
                            'material_type': Material.MaterialType.LINK,
                            'url': 'https://developer.mozilla.org/en-US/docs/Learn/HTML',
                            'is_required': True,
                        },
                        {
                            'title': 'HTML5 Reference Sheet',
                            'description': 'Quick reference for HTML5 elements.',
                            'material_type': Material.MaterialType.DOCUMENT,
                            'url': 'https://example.com/html5-reference.pdf',
                        },
                    ],
                },
                {
                    'title': 'Module 2: CSS Styling',
                    'description': 'Master CSS selectors, properties, and layouts.',
                    'materials': [
                        {
                            'title': 'CSS Flexbox Tutorial',
                            'description': 'Learn modern CSS layout with Flexbox.',
                            'material_type': Material.MaterialType.VIDEO,
                            'url': 'https://www.youtube.com/watch?v=fYq5PXgSsbE',
                            'is_required': True,
                        },
                        {
                            'title': 'CSS Grid Guide',
                            'description': 'Complete guide to CSS Grid layout.',
                            'material_type': Material.MaterialType.LINK,
                            'url': 'https://css-tricks.com/snippets/css/complete-guide-grid/',
                        },
                    ],
                },
            ]

        for order, module_data in enumerate(modules_data):
            materials = module_data.pop('materials')
            module, created = Module.objects.get_or_create(
                course=course,
                order=order,
                defaults={
                    'title': module_data['title'],
                    'description': module_data['description'],
                    'is_published': True,
                }
            )

            if created:
                self.stdout.write(f'  ✓ Created module: {module.title}')

                # Create materials for this module
                for mat_order, material_data in enumerate(materials):
                    Material.objects.create(
                        module=module,
                        order=mat_order,
                        uploaded_by=instructor,
                        **material_data
                    )
                    self.stdout.write(f'    • Added material: {material_data["title"]}')

    def _create_assignments(self, course):
        """Create sample assignments for a course."""
        if course.code == 'CS101':
            assignments_data = [
                {
                    'title': 'Python Basics - Homework 1',
                    'description': 'Complete the following programming exercises:\n1. Write a function to calculate factorial\n2. Create a program to check if a number is prime\n3. Implement a simple calculator',
                    'assignment_type': Assignment.AssignmentType.HOMEWORK,
                    'total_points': 50,
                    'due_date': timezone.now() + timedelta(days=7),
                },
                {
                    'title': 'Data Structures Project',
                    'description': 'Build a complete TODO list application using Python classes.\n\nRequirements:\n- Add, remove, and list tasks\n- Mark tasks as complete\n- Save/load from file\n- Use proper OOP principles',
                    'assignment_type': Assignment.AssignmentType.PROJECT,
                    'total_points': 100,
                    'due_date': timezone.now() + timedelta(days=21),
                },
                {
                    'title': 'Algorithm Analysis Essay',
                    'description': 'Write a 1500-word essay comparing different sorting algorithms (bubble sort, merge sort, quick sort). Discuss time complexity and real-world applications.',
                    'assignment_type': Assignment.AssignmentType.ESSAY,
                    'total_points': 75,
                    'due_date': timezone.now() + timedelta(days=14),
                },
            ]
        else:  # WEB201
            assignments_data = [
                {
                    'title': 'Build a Personal Portfolio',
                    'description': 'Create a responsive personal portfolio website using HTML and CSS.\n\nRequirements:\n- At least 3 pages (Home, About, Contact)\n- Mobile responsive design\n- Use CSS Grid or Flexbox\n- Include images and proper semantic HTML',
                    'assignment_type': Assignment.AssignmentType.PROJECT,
                    'total_points': 100,
                    'due_date': timezone.now() + timedelta(days=14),
                },
                {
                    'title': 'CSS Layout Exercise',
                    'description': 'Recreate the provided design mockup using HTML and CSS. Focus on proper layout techniques.',
                    'assignment_type': Assignment.AssignmentType.HOMEWORK,
                    'total_points': 50,
                    'due_date': timezone.now() + timedelta(days=7),
                },
            ]

        for assignment_data in assignments_data:
            assignment, created = Assignment.objects.get_or_create(
                course=course,
                title=assignment_data['title'],
                defaults=assignment_data
            )
            if created:
                self.stdout.write(f'  ✓ Created assignment: {assignment.title}')

    def _create_quizzes(self, course):
        """Create sample quizzes with questions for a course."""
        if course.code == 'CS101':
            quizzes_data = [
                {
                    'title': 'Python Fundamentals Quiz',
                    'description': 'Test your knowledge of Python basics.',
                    'total_points': 100,
                    'due_date': timezone.now() + timedelta(days=5),
                    'quiz_settings': {
                        'time_limit': 30,
                        'allow_multiple_attempts': True,
                        'max_attempts': 3,
                        'show_correct_answers': True,
                        'pass_percentage': 70,
                    },
                    'questions': [
                        {
                            'question_text': 'What is the output of: print(type(5.0))?',
                            'question_type': Question.QuestionType.MULTIPLE_CHOICE,
                            'points': 10,
                            'order': 1,
                            'explanation': 'In Python, numbers with decimal points are float type, even if the decimal is .0',
                            'choices': [
                                {'choice_text': "<class 'float'>", 'is_correct': True, 'order': 1},
                                {'choice_text': "<class 'int'>", 'is_correct': False, 'order': 2},
                                {'choice_text': "<class 'double'>", 'is_correct': False, 'order': 3},
                                {'choice_text': "<class 'number'>", 'is_correct': False, 'order': 4},
                            ],
                        },
                        {
                            'question_text': 'Python is a dynamically typed language.',
                            'question_type': Question.QuestionType.TRUE_FALSE,
                            'points': 5,
                            'order': 2,
                            'explanation': 'Python is dynamically typed, meaning you don\'t need to declare variable types.',
                            'choices': [
                                {'choice_text': 'True', 'is_correct': True, 'order': 1},
                                {'choice_text': 'False', 'is_correct': False, 'order': 2},
                            ],
                        },
                        {
                            'question_text': 'What keyword is used to define a function in Python?',
                            'question_type': Question.QuestionType.SHORT_ANSWER,
                            'points': 5,
                            'order': 3,
                            'explanation': 'The "def" keyword is used to define functions in Python.',
                            'choices': [
                                {'choice_text': 'def', 'is_correct': True, 'order': 1},
                            ],
                        },
                        {
                            'question_text': 'Which of the following is a valid Python variable name?',
                            'question_type': Question.QuestionType.MULTIPLE_CHOICE,
                            'points': 10,
                            'order': 4,
                            'explanation': 'Python variables must start with a letter or underscore, and can contain letters, numbers, and underscores.',
                            'choices': [
                                {'choice_text': 'my_variable', 'is_correct': True, 'order': 1},
                                {'choice_text': '2fast', 'is_correct': False, 'order': 2},
                                {'choice_text': 'my-variable', 'is_correct': False, 'order': 3},
                                {'choice_text': 'class', 'is_correct': False, 'order': 4},
                            ],
                        },
                        {
                            'question_text': 'Lists in Python are mutable (can be changed).',
                            'question_type': Question.QuestionType.TRUE_FALSE,
                            'points': 5,
                            'order': 5,
                            'explanation': 'Lists are mutable, meaning you can modify them after creation. Tuples are immutable.',
                            'choices': [
                                {'choice_text': 'True', 'is_correct': True, 'order': 1},
                                {'choice_text': 'False', 'is_correct': False, 'order': 2},
                            ],
                        },
                    ],
                },
            ]
        else:  # WEB201
            quizzes_data = [
                {
                    'title': 'HTML & CSS Basics Quiz',
                    'description': 'Test your understanding of HTML and CSS fundamentals.',
                    'total_points': 100,
                    'due_date': timezone.now() + timedelta(days=5),
                    'quiz_settings': {
                        'time_limit': 25,
                        'allow_multiple_attempts': True,
                        'max_attempts': 2,
                        'show_correct_answers': True,
                        'pass_percentage': 75,
                    },
                    'questions': [
                        {
                            'question_text': 'Which HTML tag is used to define an internal style sheet?',
                            'question_type': Question.QuestionType.MULTIPLE_CHOICE,
                            'points': 10,
                            'order': 1,
                            'explanation': 'The <style> tag is used to define internal CSS within an HTML document.',
                            'choices': [
                                {'choice_text': '<style>', 'is_correct': True, 'order': 1},
                                {'choice_text': '<css>', 'is_correct': False, 'order': 2},
                                {'choice_text': '<script>', 'is_correct': False, 'order': 3},
                                {'choice_text': '<link>', 'is_correct': False, 'order': 4},
                            ],
                        },
                        {
                            'question_text': 'CSS stands for Cascading Style Sheets.',
                            'question_type': Question.QuestionType.TRUE_FALSE,
                            'points': 5,
                            'order': 2,
                            'explanation': 'CSS stands for Cascading Style Sheets, used to style HTML elements.',
                            'choices': [
                                {'choice_text': 'True', 'is_correct': True, 'order': 1},
                                {'choice_text': 'False', 'is_correct': False, 'order': 2},
                            ],
                        },
                        {
                            'question_text': 'What CSS property is used to change the text color?',
                            'question_type': Question.QuestionType.SHORT_ANSWER,
                            'points': 5,
                            'order': 3,
                            'explanation': 'The "color" property sets the text color in CSS.',
                            'choices': [
                                {'choice_text': 'color', 'is_correct': True, 'order': 1},
                            ],
                        },
                        {
                            'question_text': 'Which HTML element is used for the largest heading?',
                            'question_type': Question.QuestionType.MULTIPLE_CHOICE,
                            'points': 10,
                            'order': 4,
                            'explanation': 'HTML headings range from <h1> (largest) to <h6> (smallest).',
                            'choices': [
                                {'choice_text': '<h1>', 'is_correct': True, 'order': 1},
                                {'choice_text': '<h6>', 'is_correct': False, 'order': 2},
                                {'choice_text': '<heading>', 'is_correct': False, 'order': 3},
                                {'choice_text': '<head>', 'is_correct': False, 'order': 4},
                            ],
                        },
                        {
                            'question_text': 'The <div> element is a block-level element.',
                            'question_type': Question.QuestionType.TRUE_FALSE,
                            'points': 5,
                            'order': 5,
                            'explanation': '<div> is a block-level element that takes up the full width available.',
                            'choices': [
                                {'choice_text': 'True', 'is_correct': True, 'order': 1},
                                {'choice_text': 'False', 'is_correct': False, 'order': 2},
                            ],
                        },
                    ],
                },
            ]

        for quiz_data in quizzes_data:
            questions_data = quiz_data.pop('questions')
            quiz_settings = quiz_data.pop('quiz_settings')

            # Create assignment for the quiz
            assignment, created = Assignment.objects.get_or_create(
                course=course,
                title=quiz_data['title'],
                defaults={
                    **quiz_data,
                    'assignment_type': Assignment.AssignmentType.QUIZ,
                }
            )

            if created:
                self.stdout.write(f'  ✓ Created quiz assignment: {assignment.title}')

                # Create quiz
                quiz = Quiz.objects.create(
                    assignment=assignment,
                    **quiz_settings
                )
                self.stdout.write(f'    • Created quiz with {len(questions_data)} questions')

                # Create questions and choices
                for question_data in questions_data:
                    choices_data = question_data.pop('choices')

                    question = Question.objects.create(
                        quiz=quiz,
                        **question_data
                    )

                    # Create choices
                    for choice_data in choices_data:
                        QuestionChoice.objects.create(
                            question=question,
                            **choice_data
                        )

                self.stdout.write(f'    • Added {len(questions_data)} questions with choices')
