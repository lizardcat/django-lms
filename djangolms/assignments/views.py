from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from djangolms.courses.models import Course, Enrollment
from .models import Assignment, Submission
from .forms import AssignmentForm, SubmissionForm, GradeSubmissionForm


@login_required
def assignment_list(request, course_id):
    """
    List all assignments for a course.
    """
    course = get_object_or_404(Course, id=course_id)

    # Check if user has access to this course
    is_instructor = request.user == course.instructor
    is_enrolled = Enrollment.objects.filter(student=request.user, course=course, status='ENROLLED').exists()

    if not (is_instructor or is_enrolled):
        messages.error(request, 'You do not have access to this course.')
        return redirect('course_detail', course_id=course.id)

    assignments = Assignment.objects.filter(course=course).order_by('-due_date')

    # For students, show submission status
    if request.user.is_student:
        for assignment in assignments:
            assignment.user_submission = Submission.objects.filter(assignment=assignment, student=request.user).first()

    context = {
        'course': course,
        'assignments': assignments,
        'is_instructor': is_instructor,
    }
    return render(request, 'assignments/assignment_list.html', context)


@login_required
def assignment_detail(request, assignment_id):
    """
    Display assignment details and submission status.
    """
    assignment = get_object_or_404(Assignment, id=assignment_id)
    course = assignment.course

    # Check access
    is_instructor = request.user == course.instructor
    is_enrolled = Enrollment.objects.filter(student=request.user, course=course, status='ENROLLED').exists()

    if not (is_instructor or is_enrolled):
        messages.error(request, 'You do not have access to this assignment.')
        return redirect('course_detail', course_id=course.id)

    submission = None
    if request.user.is_student:
        submission = Submission.objects.filter(assignment=assignment, student=request.user).first()

    context = {
        'assignment': assignment,
        'course': course,
        'submission': submission,
        'is_instructor': is_instructor,
    }
    return render(request, 'assignments/assignment_detail.html', context)


@login_required
def assignment_create(request, course_id):
    """
    Create a new assignment (instructors only).
    """
    course = get_object_or_404(Course, id=course_id)

    if request.user != course.instructor:
        messages.error(request, 'Only the course instructor can create assignments.')
        return redirect('course_detail', course_id=course.id)

    if request.method == 'POST':
        form = AssignmentForm(request.POST, request.FILES)
        if form.is_valid():
            assignment = form.save(commit=False)
            assignment.course = course
            assignment.save()
            messages.success(request, f'Assignment "{assignment.title}" created successfully!')
            return redirect('assignment_detail', assignment_id=assignment.id)
    else:
        form = AssignmentForm()

    context = {
        'form': form,
        'course': course,
        'action': 'Create'
    }
    return render(request, 'assignments/assignment_form.html', context)


@login_required
def assignment_edit(request, assignment_id):
    """
    Edit an existing assignment (course instructor only).
    """
    assignment = get_object_or_404(Assignment, id=assignment_id)
    course = assignment.course

    if request.user != course.instructor:
        messages.error(request, 'Only the course instructor can edit assignments.')
        return redirect('assignment_detail', assignment_id=assignment.id)

    if request.method == 'POST':
        form = AssignmentForm(request.POST, request.FILES, instance=assignment)
        if form.is_valid():
            form.save()
            messages.success(request, f'Assignment "{assignment.title}" updated successfully!')
            return redirect('assignment_detail', assignment_id=assignment.id)
    else:
        form = AssignmentForm(instance=assignment)

    context = {
        'form': form,
        'course': course,
        'assignment': assignment,
        'action': 'Edit'
    }
    return render(request, 'assignments/assignment_form.html', context)


@login_required
def assignment_delete(request, assignment_id):
    """
    Delete an assignment (course instructor only).
    """
    assignment = get_object_or_404(Assignment, id=assignment_id)
    course = assignment.course

    if request.user != course.instructor:
        messages.error(request, 'Only the course instructor can delete assignments.')
        return redirect('assignment_detail', assignment_id=assignment.id)

    if request.method == 'POST':
        assignment.delete()
        messages.success(request, 'Assignment deleted successfully.')
        return redirect('assignment_list', course_id=course.id)

    return render(request, 'assignments/assignment_confirm_delete.html', {'assignment': assignment, 'course': course})


@login_required
def submit_assignment(request, assignment_id):
    """
    Submit an assignment (students only).
    """
    assignment = get_object_or_404(Assignment, id=assignment_id)
    course = assignment.course

    if not request.user.is_student:
        messages.error(request, 'Only students can submit assignments.')
        return redirect('assignment_detail', assignment_id=assignment.id)

    # Check enrollment
    if not Enrollment.objects.filter(student=request.user, course=course, status='ENROLLED').exists():
        messages.error(request, 'You must be enrolled in this course to submit assignments.')
        return redirect('course_detail', course_id=course.id)

    # Check if already submitted
    existing_submission = Submission.objects.filter(assignment=assignment, student=request.user).first()

    # Check if late submission is allowed
    if assignment.is_overdue and not assignment.allow_late_submission:
        messages.error(request, 'This assignment is past due and late submissions are not allowed.')
        return redirect('assignment_detail', assignment_id=assignment.id)

    if request.method == 'POST':
        form = SubmissionForm(request.POST, request.FILES, instance=existing_submission)
        if form.is_valid():
            submission = form.save(commit=False)
            submission.assignment = assignment
            submission.student = request.user
            submission.save()

            if existing_submission:
                messages.success(request, 'Your submission has been updated!')
            else:
                messages.success(request, 'Assignment submitted successfully!')
            return redirect('assignment_detail', assignment_id=assignment.id)
    else:
        form = SubmissionForm(instance=existing_submission)

    context = {
        'form': form,
        'assignment': assignment,
        'course': course,
        'existing_submission': existing_submission,
    }
    return render(request, 'assignments/submit_assignment.html', context)


@login_required
def view_submissions(request, assignment_id):
    """
    View all submissions for an assignment (instructor only).
    """
    assignment = get_object_or_404(Assignment, id=assignment_id)
    course = assignment.course

    if request.user != course.instructor:
        messages.error(request, 'Only the course instructor can view submissions.')
        return redirect('assignment_detail', assignment_id=assignment.id)

    submissions = Submission.objects.filter(assignment=assignment).select_related('student').order_by('-submitted_at')

    context = {
        'assignment': assignment,
        'course': course,
        'submissions': submissions,
    }
    return render(request, 'assignments/view_submissions.html', context)


@login_required
def grade_submission(request, submission_id):
    """
    Grade a student submission (instructor only).
    """
    submission = get_object_or_404(Submission, id=submission_id)
    assignment = submission.assignment
    course = assignment.course

    if request.user != course.instructor:
        messages.error(request, 'Only the course instructor can grade submissions.')
        return redirect('assignment_detail', assignment_id=assignment.id)

    if request.method == 'POST':
        form = GradeSubmissionForm(request.POST, instance=submission)
        if form.is_valid():
            graded_submission = form.save(commit=False)
            graded_submission.graded = True
            graded_submission.graded_by = request.user
            graded_submission.graded_at = timezone.now()
            graded_submission.save()
            messages.success(request, f'Submission by {submission.student.username} has been graded.')
            return redirect('view_submissions', assignment_id=assignment.id)
    else:
        form = GradeSubmissionForm(instance=submission)

    context = {
        'form': form,
        'submission': submission,
        'assignment': assignment,
        'course': course,
    }
    return render(request, 'assignments/grade_submission.html', context)
