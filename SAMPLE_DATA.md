# Sample Data for Django LMS

This document describes the sample data that can be generated for testing and demonstration purposes.

## Creating Sample Data

Run the management command to populate your LMS with sample content:

```bash
python manage.py create_sample_data
```

## What Gets Created

### 1. Sample Instructor
- **Username:** `prof_smith`
- **Password:** `instructor123`
- **Email:** prof.smith@university.edu
- **Name:** John Smith
- **Role:** Instructor

### 2. Sample Courses

#### CS101 - Introduction to Computer Science
**Modules & Materials:**
- **Week 1: Introduction to Programming**
  - Course Syllabus (Document/Link)
  - Introduction to Python - Video Lecture (YouTube embed)
  - Python Official Documentation (External link)

- **Week 2: Variables and Data Types**
  - Variables and Data Types - Lecture Slides (Presentation)
  - Python Type System Tutorial (External link)

- **Week 3: Control Flow**
  - Control Flow - Video Lecture (Required)
  - Practice Exercises (File download)

**Assignments:**
1. **Python Basics - Homework 1** (50 points)
   - Programming exercises on functions and control flow
   - Due: 7 days from creation

2. **Data Structures Project** (100 points)
   - Build a TODO list application
   - Due: 21 days from creation

3. **Algorithm Analysis Essay** (75 points)
   - 1500-word essay on sorting algorithms
   - Due: 14 days from creation

**Quiz: Python Fundamentals Quiz** (30 minutes, 3 attempts allowed)
- Question 1: Multiple Choice - Output of type(5.0) (10 pts)
- Question 2: True/False - Python is dynamically typed (5 pts)
- Question 3: Short Answer - Function definition keyword (5 pts)
- Question 4: Multiple Choice - Valid variable names (10 pts)
- Question 5: True/False - Lists are mutable (5 pts)
- **Pass percentage:** 70%
- **Total:** 35 points

#### WEB201 - Web Development Fundamentals
**Modules & Materials:**
- **Module 1: HTML Fundamentals**
  - HTML Basics - MDN Guide (Required link)
  - HTML5 Reference Sheet (Document)

- **Module 2: CSS Styling**
  - CSS Flexbox Tutorial (Required video)
  - CSS Grid Guide (External link)

**Assignments:**
1. **Build a Personal Portfolio** (100 points)
   - Responsive website with 3+ pages
   - Due: 14 days from creation

2. **CSS Layout Exercise** (50 points)
   - Recreate design mockup
   - Due: 7 days from creation

**Quiz: HTML & CSS Basics Quiz** (25 minutes, 2 attempts allowed)
- Question 1: Multiple Choice - Internal style sheet tag (10 pts)
- Question 2: True/False - CSS stands for Cascading Style Sheets (5 pts)
- Question 3: Short Answer - Text color property (5 pts)
- Question 4: Multiple Choice - Largest heading element (10 pts)
- Question 5: True/False - <div> is block-level (5 pts)
- **Pass percentage:** 75%
- **Total:** 35 points

## Features Demonstrated

### Course Materials Library
- ✅ **Multiple material types:** Documents, Videos, Links, Presentations, Files
- ✅ **Required materials:** Some materials marked as required for completion
- ✅ **External content:** Links to YouTube, MDN, Real Python, CSS-Tricks
- ✅ **Organized by modules:** Content structured by weeks/topics
- ✅ **Video embeds:** YouTube embed codes included

### Quiz Auto-Grading
- ✅ **Multiple question types:** Multiple choice, True/False, Short answer
- ✅ **Points system:** Each question has assigned points
- ✅ **Time limits:** 25-30 minute quizzes
- ✅ **Multiple attempts:** 2-3 attempts allowed per quiz
- ✅ **Answer explanations:** Each question includes an explanation
- ✅ **Pass/fail thresholds:** 70-75% required to pass
- ✅ **Show correct answers:** Students can see correct answers after submission

### Assignment Types
- ✅ **Homework:** Short programming exercises
- ✅ **Projects:** Larger applications requiring multiple skills
- ✅ **Essays:** Written assignments with word count requirements
- ✅ **Quizzes:** Auto-graded assessments

## Testing the Features

### 1. Log in as Instructor
```
Username: prof_smith
Password: instructor123
```

### 2. View Courses
Navigate to Django Admin → Courses to see CS101 and WEB201

### 3. Browse Materials
Go to Courses → Modules to see organized course content with materials

### 4. Review Quizzes
Check Assignments → Quiz to see quiz questions and settings

### 5. Take a Quiz (as Student)
1. Create a student account
2. Enroll in CS101 or WEB201
3. Navigate to the quiz
4. Answer questions
5. Submit to see auto-grading in action

### 6. View Quiz Results
Instructors can view all quiz attempts in Admin → Quiz Attempts

## Customization

The management command is idempotent - you can run it multiple times safely. It checks if data already exists before creating new records.

## Clearing Sample Data

To remove sample data and start fresh:

```bash
# Delete through Django admin or shell
python manage.py shell
>>> from djangolms.courses.models import Course
>>> Course.objects.filter(code__in=['CS101', 'WEB201']).delete()
```

## Next Steps

After creating sample data:

1. **Create student accounts** to test enrollment and quiz-taking
2. **Upload actual files** to replace the example URLs
3. **Customize quiz questions** for your specific courses
4. **Add more modules** as your course progresses
5. **Configure email notifications** to alert students of new materials

## Notes

- All YouTube links point to real educational videos
- External links are to legitimate learning resources (MDN, Real Python, CSS-Tricks)
- File URLs use example.com placeholders - replace with actual files
- Due dates are set relative to creation time (5-21 days ahead)
- Materials track view counts and engagement for analytics
