# USIU-A Sample Data Guide

## Overview

This guide explains how to use the comprehensive sample data generator for USIU-A School of Science.

## Quick Start

### Generate Sample Data

Run the following command to create all sample data:

```bash
python manage.py create_usiu_sample_data
```

### Clear and Regenerate

To clear existing data and create fresh sample data:

```bash
python manage.py create_usiu_sample_data --clear
```

**⚠️ Warning**: The `--clear` flag will delete all existing courses, users (except superusers), enrollments, and course content!

## What Gets Created

### 👨‍🏫 Instructors (10)

Kenyan instructors from various departments:

| Name | Username | Email | Department |
|------|----------|-------|------------|
| Dr. James Kamau | james.kamau | james.kamau@usiu.ac.ke | Computer Science |
| Dr. Grace Wanjiru | grace.wanjiru | grace.wanjiru@usiu.ac.ke | Mathematics |
| Dr. David Ochieng | david.ochieng | david.ochieng@usiu.ac.ke | Physics |
| Dr. Mary Akinyi | mary.akinyi | mary.akinyi@usiu.ac.ke | Chemistry |
| Dr. Peter Mwangi | peter.mwangi | peter.mwangi@usiu.ac.ke | Biology |
| Dr. Sarah Njeri | sarah.njeri | sarah.njeri@usiu.ac.ke | Statistics |
| Dr. John Otieno | john.otieno | john.otieno@usiu.ac.ke | Computer Science |
| Dr. Ruth Wangari | ruth.wangari | ruth.wangari@usiu.ac.ke | Mathematics |
| Dr. Daniel Kipchoge | daniel.kipchoge | daniel.kipchoge@usiu.ac.ke | Environmental Science |
| Dr. Lucy Mutua | lucy.mutua | lucy.mutua@usiu.ac.ke | Information Systems |

**Password for all instructors**: `instructor123`

### 👨‍🎓 Students (50)

50 students with authentic Kenyan names. Examples:
- Brian Kimani (brian.kimani)
- Faith Chebet (faith.chebet)
- Kevin Omondi (kevin.omondi)
- Nancy Wambui (nancy.wambui)
- Emmanuel Kiprop (emmanuel.kiprop)
- And 45 more...

**Password for all students**: `student123`

### 📚 Courses (20)

#### Computer Science (4 courses)
- **CS101**: Introduction to Programming
- **CS201**: Data Structures and Algorithms
- **CS301**: Database Management Systems
- **CS401**: Web Application Development

#### Mathematics (4 courses)
- **MATH101**: Calculus I
- **MATH201**: Linear Algebra
- **MATH301**: Probability and Statistics
- **MATH401**: Differential Equations

#### Physics (3 courses)
- **PHYS101**: General Physics I
- **PHYS201**: Electricity and Magnetism
- **PHYS301**: Modern Physics

#### Chemistry (3 courses)
- **CHEM101**: General Chemistry
- **CHEM201**: Organic Chemistry
- **CHEM301**: Analytical Chemistry

#### Biology (3 courses)
- **BIO101**: Introduction to Biology
- **BIO201**: Molecular Biology
- **BIO301**: Microbiology

#### Statistics & Data Science (2 courses)
- **STAT201**: Statistical Methods
- **DATA301**: Introduction to Data Science

#### Environmental Science (1 course)
- **ENV201**: Environmental Science

### 📖 Course Content

Each course includes:

**Modules**: 4-6 modules per course
- Well-structured learning modules
- Clear learning objectives
- Sequential ordering

**Materials**: 2-4 materials per module
- Lecture notes
- Lab exercises
- Reading materials
- Video tutorials
- Case studies

**Assignments**: 1 assignment per module
- Detailed instructions
- Grading criteria
- Submission guidelines
- 100 points each

**Quizzes**: 1 quiz per module
- 5-8 multiple choice questions
- 30-minute time limit
- 2 attempts allowed
- 10 points per question
- Randomized questions
- Shows correct answers after submission

### 🎓 Enrollments

- Each student is automatically enrolled in 4-6 random courses
- Realistic distribution across departments
- Active enrollment status

## Login Information

### Format

- **Username**: `first_name.last_name` (all lowercase)
- **Email**: `username@usiu.ac.ke` (instructors) or `username@student.usiu.ac.ke` (students)

### Example Logins

**Instructor Example**:
```
Username: james.kamau
Password: instructor123
Email: james.kamau@usiu.ac.ke
```

**Student Example**:
```
Username: brian.kimani
Password: student123
Email: brian.kimani@student.usiu.ac.ke
```

## Testing the Data

### As an Instructor

1. **Login**: Use any instructor credentials (e.g., `james.kamau` / `instructor123`)
2. **View Courses**: Navigate to "My Courses" to see assigned courses
3. **Manage Content**: Access modules, materials, assignments, and quizzes
4. **View Enrollments**: See which students are enrolled
5. **Create Livestream**: Test the livestreaming feature
6. **Grade Assignments**: Review and grade student submissions

### As a Student

1. **Login**: Use any student credentials (e.g., `brian.kimani` / `student123`)
2. **View Courses**: See all enrolled courses (4-6 courses)
3. **Access Content**: Browse modules and materials
4. **Take Quizzes**: Complete module quizzes
5. **Submit Assignments**: Upload assignment submissions
6. **Join Livestreams**: Participate in live lectures
7. **Use Chat**: Communicate with classmates

## Verification

After running the command, verify the data was created:

```bash
# Check Django admin
python manage.py runserver
# Visit http://localhost:8000/admin

# Or use Django shell
python manage.py shell
>>> from djangolms.accounts.models import User
>>> from djangolms.courses.models import Course, Enrollment
>>>
>>> # Count instructors
>>> User.objects.filter(role='INSTRUCTOR').count()
10
>>>
>>> # Count students
>>> User.objects.filter(role='STUDENT').count()
50
>>>
>>> # Count courses
>>> Course.objects.count()
20+
>>>
>>> # Count enrollments
>>> Enrollment.objects.count()
200+  # Varies due to random enrollment
```

## Customization

To customize the sample data, edit the management command:

```bash
nano djangolms/courses/management/commands/create_usiu_sample_data.py
```

You can modify:
- Instructor names and emails
- Student names and emails
- Course titles and descriptions
- Number of modules per course
- Number of materials per module
- Quiz questions and answers
- Assignment descriptions

## Troubleshooting

### Issue: "User already exists"

**Solution**: This is normal if you run the command multiple times. The command will skip existing users and create any missing data.

### Issue: "Course already exists"

**Solution**: Use the `--clear` flag to remove existing data first:
```bash
python manage.py create_usiu_sample_data --clear
```

### Issue: "No module named X"

**Solution**: Make sure you've run migrations:
```bash
python manage.py migrate
```

### Issue: Permission errors

**Solution**: Ensure your database is writable and you have proper permissions.

## Data Cleanup

To remove all sample data:

```bash
python manage.py create_usiu_sample_data --clear
```

Or manually delete from Django admin:
1. Login to admin panel
2. Navigate to each model
3. Select all and delete

## Integration with Other Features

This sample data works seamlessly with:

- **Livestreaming**: Instructors can create streams for their courses
- **Chat**: Students can chat within course rooms
- **Assignments**: Full assignment submission workflow
- **Quizzes**: Complete quiz-taking experience
- **Grading**: Instructors can grade submissions
- **Analytics**: View course statistics and student progress

## Production Use

**⚠️ Important**: This command is designed for **development and testing only**.

Do not run this in production as it:
- Creates users with default passwords
- Uses simplified email addresses
- Generates placeholder content
- May conflict with real data

For production, use proper user registration, real course content, and secure passwords.

## Support

If you encounter issues:
1. Check the command output for error messages
2. Review the Django logs
3. Verify database connections
4. Ensure all migrations are applied
5. Check for permission issues

---

**Created by**: Alex Raza
**Last Updated**: December 5, 2025
**Version**: 1.0
