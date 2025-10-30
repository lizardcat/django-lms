from django.core.management.base import BaseCommand
from djangolms.accounts.models import User
from djangolms.courses.models import Course
from datetime import date, timedelta


class Command(BaseCommand):
    help = 'Populate database with USIU Data Science & Analytics courses'

    def handle(self, *args, **kwargs):
        # Create instructor users if they don't exist
        instructors = []
        instructor_data = [
            {'username': 'prof_kimani', 'first_name': 'James', 'last_name': 'Kimani', 'email': 'j.kimani@usiu.ac.ke'},
            {'username': 'prof_wanjiru', 'first_name': 'Grace', 'last_name': 'Wanjiru', 'email': 'g.wanjiru@usiu.ac.ke'},
            {'username': 'prof_omondi', 'first_name': 'David', 'last_name': 'Omondi', 'email': 'd.omondi@usiu.ac.ke'},
            {'username': 'prof_mwangi', 'first_name': 'Sarah', 'last_name': 'Mwangi', 'email': 's.mwangi@usiu.ac.ke'},
            {'username': 'prof_ochieng', 'first_name': 'Peter', 'last_name': "Ochieng", 'email': 'p.ochieng@usiu.ac.ke'},
        ]

        for data in instructor_data:
            instructor, created = User.objects.get_or_create(
                username=data['username'],
                defaults={
                    'first_name': data['first_name'],
                    'last_name': data['last_name'],
                    'email': data['email'],
                    'role': 'INSTRUCTOR'
                }
            )
            if created:
                instructor.set_password('password123')
                instructor.save()
                self.stdout.write(self.style.SUCCESS(f'Created instructor: {instructor.username}'))
            instructors.append(instructor)

        # Course data from USIU BS in Data Science & Analytics
        courses_data = [
            # General Education Courses
            {
                'code': 'SUS1010',
                'title': 'Strategies for University Success',
                'description': 'This course provides students with essential skills and strategies for academic success at the university level. Topics include time management, study skills, critical thinking, and academic writing.',
                'category': 'General Education',
                'max_students': 40,
            },
            {
                'code': 'ENG1106',
                'title': 'Composition I',
                'description': 'An introductory course in academic writing that focuses on developing students\' ability to write clear, coherent, and well-organized essays. Emphasis on the writing process, critical reading, and rhetorical analysis.',
                'category': 'General Education',
                'max_students': 35,
            },
            {
                'code': 'IST1020',
                'title': 'Introduction to Information Systems',
                'description': 'Overview of information systems and their role in modern organizations. Topics include hardware, software, databases, networks, and the internet. Introduces students to system analysis and design.',
                'category': 'General Education',
                'max_students': 45,
            },
            {
                'code': 'MTH1109',
                'title': 'College Algebra',
                'description': 'Fundamental concepts of algebra including equations, inequalities, functions, polynomial and rational functions, exponential and logarithmic functions, and systems of equations.',
                'category': 'General Education',
                'max_students': 50,
            },
            {
                'code': 'FIL1010',
                'title': 'Fundamentals of Information Literacy',
                'description': 'Develops skills in finding, evaluating, and using information effectively. Topics include research strategies, database searching, citation styles, and ethical use of information.',
                'category': 'General Education',
                'max_students': 40,
            },
            {
                'code': 'GRM2000',
                'title': 'Introduction to Research Methods',
                'description': 'Introduction to the basic principles and methods of research. Topics include research design, data collection methods, sampling, measurement, and ethical considerations in research.',
                'category': 'General Education',
                'max_students': 35,
            },
            {
                'code': 'ENG2206',
                'title': 'Composition II',
                'description': 'Advanced course in academic writing building on Composition I. Focuses on argumentation, research writing, and critical analysis. Students produce research-based essays on complex topics.',
                'category': 'General Education',
                'max_students': 30,
            },
            {
                'code': 'CMS3700',
                'title': 'Community Service',
                'description': 'Experiential learning course where students engage in community service projects. Students reflect on their service experiences and connect them to academic concepts and social responsibility.',
                'category': 'General Education',
                'max_students': 25,
            },
            {
                'code': 'SEN4800',
                'title': 'Integrated Seminar',
                'description': 'Capstone seminar integrating knowledge from various disciplines. Students engage in critical discussions, present research, and reflect on their academic journey and future career paths.',
                'category': 'General Education',
                'max_students': 30,
            },

            # Data Science/Computer Science/IT Courses
            {
                'code': 'DSA1060',
                'title': 'Introduction to Data Science',
                'description': 'Introduction to the field of data science, including data collection, cleaning, exploration, and visualization. Overview of statistical thinking and machine learning concepts.',
                'category': 'Data Science Core',
                'max_students': 40,
            },
            {
                'code': 'DSA1080',
                'title': 'Programming for Data Science',
                'description': 'Introduction to programming using Python for data science applications. Topics include data structures, control flow, functions, and libraries such as NumPy, Pandas, and Matplotlib.',
                'category': 'Data Science Core',
                'max_students': 35,
            },
            {
                'code': 'APT1050',
                'title': 'Database Systems',
                'description': 'Fundamentals of database design and management. Topics include relational database model, SQL, normalization, database design, and introduction to NoSQL databases.',
                'category': 'Data Science Core',
                'max_students': 40,
            },
            {
                'code': 'APT2060',
                'title': 'Data Structures and Algorithms',
                'description': 'Study of fundamental data structures (arrays, linked lists, stacks, queues, trees, graphs) and algorithms (sorting, searching, recursion). Analysis of algorithm complexity.',
                'category': 'Data Science Core',
                'max_students': 35,
            },
            {
                'code': 'APT3040',
                'title': 'Object Oriented Analysis, Design & Programming',
                'description': 'Principles of object-oriented programming including encapsulation, inheritance, and polymorphism. UML modeling, design patterns, and software development methodologies.',
                'category': 'Data Science Core',
                'max_students': 30,
            },
            {
                'code': 'DSA2040',
                'title': 'Data Warehousing and Mining',
                'description': 'Concepts and techniques for building data warehouses and mining large datasets. Topics include ETL processes, OLAP, data mining algorithms, and pattern discovery.',
                'category': 'Data Science Core',
                'max_students': 30,
            },
            {
                'code': 'DSA2050',
                'title': 'Data Science Methodology',
                'description': 'Systematic approach to data science projects. Topics include problem definition, data understanding, data preparation, modeling, evaluation, and deployment using industry-standard frameworks.',
                'category': 'Data Science Core',
                'max_students': 35,
            },
            {
                'code': 'DSA2020',
                'title': 'Artificial Intelligence',
                'description': 'Introduction to artificial intelligence concepts and techniques. Topics include search algorithms, knowledge representation, reasoning, planning, and introduction to machine learning.',
                'category': 'Data Science Core',
                'max_students': 35,
            },
            {
                'code': 'DSA3020',
                'title': 'Principles of Machine Learning',
                'description': 'Comprehensive introduction to machine learning algorithms and applications. Topics include supervised learning, unsupervised learning, model evaluation, and feature engineering.',
                'category': 'Data Science Core',
                'max_students': 30,
            },
            {
                'code': 'DSA3050',
                'title': 'Business Intelligence and Data Visualization',
                'description': 'Techniques for transforming data into actionable business insights. Topics include data visualization principles, dashboard design, and BI tools like Tableau and Power BI.',
                'category': 'Data Science Core',
                'max_students': 30,
            },
            {
                'code': 'DSA3030',
                'title': 'Big Data Architecture',
                'description': 'Architecture and infrastructure for big data systems. Topics include distributed computing, Hadoop ecosystem, MapReduce, Spark, and cloud computing platforms.',
                'category': 'Data Science Core',
                'max_students': 25,
            },
            {
                'code': 'DSA4010',
                'title': 'Big Data Analytics',
                'description': 'Advanced techniques for analyzing massive datasets. Topics include streaming data, real-time analytics, NoSQL databases, and scalable machine learning algorithms.',
                'category': 'Data Science Core',
                'max_students': 25,
            },
            {
                'code': 'DSA3900',
                'title': 'Data Science Project Proposal',
                'description': 'Students develop a comprehensive proposal for their capstone data science project. Includes literature review, methodology design, and project planning.',
                'category': 'Data Science Core',
                'max_students': 20,
            },
            {
                'code': 'DSA4020',
                'title': 'Natural Language Processing',
                'description': 'Techniques for processing and analyzing human language data. Topics include text preprocessing, sentiment analysis, topic modeling, and transformer models.',
                'category': 'Data Science Core',
                'max_students': 25,
            },
            {
                'code': 'DSA4030',
                'title': 'Big Data Security and Ethics',
                'description': 'Security challenges and ethical considerations in big data. Topics include privacy, data protection, bias in algorithms, and responsible AI development.',
                'category': 'Data Science Core',
                'max_students': 30,
            },
            {
                'code': 'DSA4050',
                'title': 'Deep Learning',
                'description': 'Advanced neural network architectures and deep learning techniques. Topics include CNNs, RNNs, GANs, transfer learning, and applications in computer vision and NLP.',
                'category': 'Data Science Core',
                'max_students': 25,
            },

            # Mathematics and Statistics Courses
            {
                'code': 'MTH1040',
                'title': 'Linear Algebra',
                'description': 'Vector spaces, matrices, linear transformations, eigenvalues and eigenvectors, and applications to data science and machine learning.',
                'category': 'Mathematics',
                'max_students': 40,
            },
            {
                'code': 'STA1020',
                'title': 'Probability and Statistics I',
                'description': 'Introduction to probability theory and statistical methods. Topics include probability distributions, random variables, expectation, variance, and basic inferential statistics.',
                'category': 'Statistics',
                'max_students': 40,
            },
            {
                'code': 'MTH1110',
                'title': 'Calculus',
                'description': 'Limits, continuity, derivatives, integrals, and their applications. Includes both single-variable and multivariable calculus concepts relevant to data science.',
                'category': 'Mathematics',
                'max_students': 45,
            },
            {
                'code': 'MTH2215',
                'title': 'Discrete Mathematics',
                'description': 'Mathematical structures and logic used in computer science. Topics include sets, relations, functions, graphs, trees, and combinatorics.',
                'category': 'Mathematics',
                'max_students': 35,
            },
            {
                'code': 'MTH1050',
                'title': 'Differential Equations',
                'description': 'Ordinary differential equations and their solutions. Applications to modeling real-world phenomena in science, engineering, and data analysis.',
                'category': 'Mathematics',
                'max_students': 30,
            },
            {
                'code': 'MTH2030',
                'title': 'Numerical Analysis and its Applications',
                'description': 'Numerical methods for solving mathematical problems. Topics include root finding, interpolation, numerical integration, and solving differential equations.',
                'category': 'Mathematics',
                'max_students': 30,
            },
            {
                'code': 'STA1040',
                'title': 'Statistical Computing',
                'description': 'Introduction to statistical programming using R. Topics include data manipulation, statistical graphics, simulation, and implementation of statistical methods.',
                'category': 'Statistics',
                'max_students': 35,
            },
            {
                'code': 'STA2010',
                'title': 'Probability and Statistics II',
                'description': 'Continuation of Probability and Statistics I. Advanced topics in probability theory, sampling distributions, hypothesis testing, and regression analysis.',
                'category': 'Statistics',
                'max_students': 35,
            },
            {
                'code': 'MTH2020',
                'title': 'Optimization Techniques',
                'description': 'Methods for finding optimal solutions to mathematical problems. Topics include linear programming, nonlinear optimization, and constrained optimization.',
                'category': 'Mathematics',
                'max_students': 30,
            },
            {
                'code': 'MTH1060',
                'title': 'Analytical and Computational Techniques',
                'description': 'Advanced analytical methods and computational approaches for solving complex mathematical problems arising in data science applications.',
                'category': 'Mathematics',
                'max_students': 30,
            },
            {
                'code': 'STA2030',
                'title': 'Statistical Inference',
                'description': 'Theory and methods of statistical inference. Topics include estimation, hypothesis testing, confidence intervals, and asymptotic theory.',
                'category': 'Statistics',
                'max_students': 30,
            },
            {
                'code': 'STA2060',
                'title': 'Stochastic Processes',
                'description': 'Introduction to random processes evolving over time. Topics include Markov chains, Poisson processes, and applications to modeling sequential data.',
                'category': 'Statistics',
                'max_students': 25,
            },
            {
                'code': 'STA3020',
                'title': 'Multivariate Statistical Analysis',
                'description': 'Statistical methods for analyzing multiple variables simultaneously. Topics include PCA, factor analysis, discriminant analysis, and clustering.',
                'category': 'Statistics',
                'max_students': 25,
            },
            {
                'code': 'STA3010',
                'title': 'Statistical Modeling',
                'description': 'Advanced techniques for building and validating statistical models. Topics include linear models, generalized linear models, and model selection.',
                'category': 'Statistics',
                'max_students': 25,
            },
            {
                'code': 'STA3040',
                'title': 'Mathematical Modeling and Simulation',
                'description': 'Techniques for building mathematical models of real-world systems and simulating their behavior. Applications to various domains including finance and biology.',
                'category': 'Statistics',
                'max_students': 25,
            },
            {
                'code': 'MTH3010',
                'title': 'Mathematical Finance',
                'description': 'Mathematical models and methods used in finance. Topics include portfolio theory, option pricing, risk management, and stochastic calculus.',
                'category': 'Mathematics',
                'max_students': 25,
            },
            {
                'code': 'STA3050',
                'title': 'Time Series Analysis and Forecasting',
                'description': 'Methods for analyzing temporal data and making predictions. Topics include ARIMA models, exponential smoothing, and forecasting techniques.',
                'category': 'Statistics',
                'max_students': 25,
            },
            {
                'code': 'STA4030',
                'title': 'Bayesian Inference and Decision Theory',
                'description': 'Bayesian approach to statistical inference and decision making. Topics include prior and posterior distributions, MCMC methods, and Bayesian model comparison.',
                'category': 'Statistics',
                'max_students': 20,
            },
        ]

        # Create courses
        created_count = 0
        updated_count = 0

        for i, course_data in enumerate(courses_data):
            instructor = instructors[i % len(instructors)]

            # Set realistic start and end dates
            start_date = date.today() + timedelta(days=30)
            end_date = start_date + timedelta(days=90)

            course, created = Course.objects.update_or_create(
                code=course_data['code'],
                defaults={
                    'title': course_data['title'],
                    'description': course_data['description'],
                    'instructor': instructor,
                    'status': 'PUBLISHED',
                    'max_students': course_data['max_students'],
                    'start_date': start_date,
                    'end_date': end_date,
                }
            )

            if created:
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f'Created course: {course.code} - {course.title}'))
            else:
                updated_count += 1
                self.stdout.write(self.style.WARNING(f'Updated course: {course.code} - {course.title}'))

        self.stdout.write(self.style.SUCCESS(f'\nCompleted! Created {created_count} courses, updated {updated_count} courses.'))
        self.stdout.write(self.style.SUCCESS(f'Total courses in database: {Course.objects.count()}'))
