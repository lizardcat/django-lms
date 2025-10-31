from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.db.models import Avg, Count, Q
from django.utils import timezone
import csv

from djangolms.courses.models import Course, Enrollment
from djangolms.assignments.models import Assignment, Submission
from .models import GradeScale, GradeCategory, CourseGrade, GradeHistory
from .forms import GradeScaleForm, GradeCategoryForm, GradeOverrideForm, BulkRecalculateForm


@login_required
def course_gradebook(request, course_id):
    """
    Display gradebook for a course (instructor only).
    """
    course = get_object_or_404(Course, id=course_id)

    # Check if user is the instructor
    if request.user != course.instructor:
        messages.error(request, 'Only the course instructor can view the gradebook.')
        return redirect('course_detail', course_id=course.id)

    # Get all enrolled students
    enrollments = Enrollment.objects.filter(
        course=course,
        status='ENROLLED'
    ).select_related('student').order_by('student__last_name', 'student__first_name')

    # Get or create grades for each enrollment
    grades_data = []
    for enrollment in enrollments:
        grade, created = CourseGrade.objects.get_or_create(enrollment=enrollment)
        if created or not grade.percentage:
            grade.calculate_grade()

        grades_data.append({
            'enrollment': enrollment,
            'student': enrollment.student,
            'grade': grade,
        })

    # Get grade categories
    categories = GradeCategory.objects.filter(course=course)

    # Calculate class statistics
    percentages = [g['grade'].get_display_percentage() for g in grades_data if g['grade'].get_display_percentage() is not None]
    stats = {
        'count': len(percentages),
        'average': round(sum(percentages) / len(percentages), 2) if percentages else None,
        'highest': max(percentages) if percentages else None,
        'lowest': min(percentages) if percentages else None,
    }

    context = {
        'course': course,
        'grades_data': grades_data,
        'categories': categories,
        'stats': stats,
    }
    return render(request, 'grades/gradebook.html', context)


@login_required
def student_grades(request, course_id):
    """
    Display a student's grades for a course.
    """
    course = get_object_or_404(Course, id=course_id)

    # Check if user has access
    is_instructor = request.user == course.instructor
    is_enrolled = Enrollment.objects.filter(student=request.user, course=course, status='ENROLLED').exists()

    if not (is_instructor or is_enrolled):
        messages.error(request, 'You do not have access to this course.')
        return redirect('course_detail', course_id=course.id)

    # If instructor, allow viewing any student's grades
    if is_instructor and request.GET.get('student_id'):
        from djangolms.accounts.models import User
        student = get_object_or_404(User, id=request.GET.get('student_id'))
        enrollment = get_object_or_404(Enrollment, student=student, course=course)
    else:
        student = request.user
        enrollment = get_object_or_404(Enrollment, student=student, course=course)

    # Get or create course grade
    grade, created = CourseGrade.objects.get_or_create(enrollment=enrollment)
    if created or not grade.percentage:
        grade.calculate_grade()

    # Get all assignments with student's submissions
    assignments = Assignment.objects.filter(course=course).order_by('-due_date')
    assignments_data = []

    for assignment in assignments:
        submission = Submission.objects.filter(assignment=assignment, student=student).first()
        assignments_data.append({
            'assignment': assignment,
            'submission': submission,
            'percentage': submission.percentage if submission else None,
        })

    # Get grade categories
    categories = GradeCategory.objects.filter(course=course)

    # Calculate category averages
    category_stats = []
    for category in categories:
        cat_assignments = assignments.filter(assignment_type=category.assignment_type)
        cat_submissions = Submission.objects.filter(
            assignment__in=cat_assignments,
            student=student,
            graded=True
        )

        if cat_submissions.exists():
            scores = []
            for sub in cat_submissions:
                if sub.score is not None:
                    pct = (sub.score / sub.assignment.total_points) * 100
                    scores.append(pct)

            if scores:
                avg = sum(scores) / len(scores)
                category_stats.append({
                    'category': category,
                    'average': round(avg, 2),
                    'count': len(scores),
                })

    context = {
        'course': course,
        'student': student,
        'enrollment': enrollment,
        'grade': grade,
        'assignments_data': assignments_data,
        'categories': categories,
        'category_stats': category_stats,
        'is_instructor': is_instructor,
    }
    return render(request, 'grades/student_grades.html', context)


@login_required
def grade_configuration(request, course_id):
    """
    Configure grading scale and categories (instructor only).
    """
    course = get_object_or_404(Course, id=course_id)

    if request.user != course.instructor:
        messages.error(request, 'Only the course instructor can configure grades.')
        return redirect('course_detail', course_id=course.id)

    # Get or create grade scale
    grade_scale, scale_created = GradeScale.objects.get_or_create(course=course)

    # Get all categories
    categories = GradeCategory.objects.filter(course=course)

    # Handle grade scale form
    if request.method == 'POST' and 'scale_form' in request.POST:
        scale_form = GradeScaleForm(request.POST, instance=grade_scale)
        if scale_form.is_valid():
            scale_form.save()
            messages.success(request, 'Grade scale updated successfully!')
            return redirect('grade_configuration', course_id=course.id)
    else:
        scale_form = GradeScaleForm(instance=grade_scale)

    # Handle new category form
    if request.method == 'POST' and 'category_form' in request.POST:
        category_form = GradeCategoryForm(request.POST)
        if category_form.is_valid():
            category = category_form.save(commit=False)
            category.course = course
            category.save()
            messages.success(request, f'Category "{category.name}" created successfully!')
            return redirect('grade_configuration', course_id=course.id)
    else:
        category_form = GradeCategoryForm()

    # Calculate total weight
    total_weight = sum(float(cat.weight) for cat in categories)

    context = {
        'course': course,
        'grade_scale': grade_scale,
        'scale_form': scale_form,
        'categories': categories,
        'category_form': category_form,
        'total_weight': total_weight,
    }
    return render(request, 'grades/grade_configuration.html', context)


@login_required
def delete_category(request, category_id):
    """
    Delete a grade category (instructor only).
    """
    category = get_object_or_404(GradeCategory, id=category_id)
    course = category.course

    if request.user != course.instructor:
        messages.error(request, 'Only the course instructor can delete categories.')
        return redirect('course_detail', course_id=course.id)

    if request.method == 'POST':
        category.delete()
        messages.success(request, f'Category "{category.name}" deleted successfully.')
        return redirect('grade_configuration', course_id=course.id)

    return render(request, 'grades/category_confirm_delete.html', {'category': category, 'course': course})


@login_required
def override_grade(request, enrollment_id):
    """
    Override a student's grade (instructor only).
    """
    enrollment = get_object_or_404(Enrollment, id=enrollment_id)
    course = enrollment.course

    if request.user != course.instructor:
        messages.error(request, 'Only the course instructor can override grades.')
        return redirect('course_detail', course_id=course.id)

    grade, created = CourseGrade.objects.get_or_create(enrollment=enrollment)

    if request.method == 'POST':
        form = GradeOverrideForm(request.POST, instance=grade)
        if form.is_valid():
            # Create history entry
            GradeHistory.objects.create(
                course_grade=grade,
                changed_by=request.user,
                change_type='OVERRIDE',
                old_percentage=grade.get_display_percentage(),
                new_percentage=form.cleaned_data.get('override_percentage'),
                old_letter=grade.get_display_letter(),
                new_letter=form.cleaned_data.get('override_letter'),
                reason=form.cleaned_data.get('override_reason')
            )

            # Apply override
            grade = form.save(commit=False)
            grade.is_overridden = True
            grade.overridden_by = request.user
            grade.overridden_at = timezone.now()
            grade.save()

            messages.success(request, f'Grade override applied for {enrollment.student.username}.')
            return redirect('course_gradebook', course_id=course.id)
    else:
        form = GradeOverrideForm(instance=grade)

    context = {
        'form': form,
        'enrollment': enrollment,
        'course': course,
        'grade': grade,
    }
    return render(request, 'grades/override_grade.html', context)


@login_required
def remove_override(request, grade_id):
    """
    Remove grade override and recalculate (instructor only).
    """
    grade = get_object_or_404(CourseGrade, id=grade_id)
    course = grade.enrollment.course

    if request.user != course.instructor:
        messages.error(request, 'Only the course instructor can remove overrides.')
        return redirect('course_detail', course_id=course.id)

    if request.method == 'POST':
        # Create history entry
        GradeHistory.objects.create(
            course_grade=grade,
            changed_by=request.user,
            change_type='REMOVED',
            old_percentage=grade.override_percentage,
            new_percentage=grade.percentage,
            old_letter=grade.override_letter,
            new_letter=grade.letter_grade,
            reason='Override removed, reverted to calculated grade'
        )

        # Remove override
        grade.is_overridden = False
        grade.override_percentage = None
        grade.override_letter = ''
        grade.override_reason = ''
        grade.overridden_by = None
        grade.overridden_at = None
        grade.save()

        # Recalculate
        grade.calculate_grade()

        messages.success(request, 'Grade override removed. Grade recalculated.')
        return redirect('course_gradebook', course_id=course.id)

    return render(request, 'grades/remove_override_confirm.html', {'grade': grade, 'course': course})


@login_required
def recalculate_all_grades(request, course_id):
    """
    Recalculate all grades for a course (instructor only).
    """
    course = get_object_or_404(Course, id=course_id)

    if request.user != course.instructor:
        messages.error(request, 'Only the course instructor can recalculate grades.')
        return redirect('course_detail', course_id=course.id)

    if request.method == 'POST':
        form = BulkRecalculateForm(request.POST)
        if form.is_valid():
            enrollments = Enrollment.objects.filter(course=course, status='ENROLLED')
            count = 0

            for enrollment in enrollments:
                grade, created = CourseGrade.objects.get_or_create(enrollment=enrollment)
                if not grade.is_overridden:
                    grade.calculate_grade()
                    count += 1

            messages.success(request, f'Recalculated {count} grades successfully.')
            return redirect('course_gradebook', course_id=course.id)
    else:
        form = BulkRecalculateForm()

    context = {
        'form': form,
        'course': course,
    }
    return render(request, 'grades/recalculate_confirm.html', context)


@login_required
def export_grades(request, course_id):
    """
    Export grades to CSV (instructor only).
    """
    course = get_object_or_404(Course, id=course_id)

    if request.user != course.instructor:
        messages.error(request, 'Only the course instructor can export grades.')
        return redirect('course_detail', course_id=course.id)

    # Create CSV response
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{course.code}_grades.csv"'

    writer = csv.writer(response)

    # Write header
    writer.writerow([
        'Student ID',
        'Student Name',
        'Email',
        'Percentage',
        'Letter Grade',
        'Is Overridden',
        'Last Updated'
    ])

    # Get all enrollments with grades
    enrollments = Enrollment.objects.filter(course=course, status='ENROLLED').select_related('student')

    for enrollment in enrollments:
        try:
            grade = CourseGrade.objects.get(enrollment=enrollment)
            writer.writerow([
                enrollment.student.username,
                enrollment.student.get_full_name() or enrollment.student.username,
                enrollment.student.email,
                grade.get_display_percentage() or 'N/A',
                grade.get_display_letter() or 'N/A',
                'Yes' if grade.is_overridden else 'No',
                grade.last_calculated.strftime('%Y-%m-%d %H:%M:%S')
            ])
        except CourseGrade.DoesNotExist:
            writer.writerow([
                enrollment.student.username,
                enrollment.student.get_full_name() or enrollment.student.username,
                enrollment.student.email,
                'N/A',
                'N/A',
                'No',
                'N/A'
            ])

    return response
