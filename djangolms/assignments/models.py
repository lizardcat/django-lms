from django.db import models
from django.conf import settings
from django.utils import timezone
from djangolms.courses.models import Course


class Assignment(models.Model):
    """
    Assignment model representing coursework for students to complete.
    """
    class AssignmentType(models.TextChoices):
        HOMEWORK = 'HOMEWORK', 'Homework'
        QUIZ = 'QUIZ', 'Quiz'
        PROJECT = 'PROJECT', 'Project'
        EXAM = 'EXAM', 'Exam'
        ESSAY = 'ESSAY', 'Essay'

    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='assignments',
        help_text="Course this assignment belongs to"
    )
    title = models.CharField(max_length=200, help_text="Assignment title")
    description = models.TextField(help_text="Assignment description and instructions")
    assignment_type = models.CharField(
        max_length=20,
        choices=AssignmentType.choices,
        default=AssignmentType.HOMEWORK,
        help_text="Type of assignment"
    )
    total_points = models.PositiveIntegerField(
        default=100,
        help_text="Maximum points for this assignment"
    )
    due_date = models.DateTimeField(help_text="Assignment due date")
    attachment = models.FileField(
        upload_to='assignment_files/',
        blank=True,
        null=True,
        help_text="Optional attachment (PDF, docs, etc.)"
    )
    allow_late_submission = models.BooleanField(
        default=False,
        help_text="Allow submissions after due date"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Assignment'
        verbose_name_plural = 'Assignments'
        ordering = ['-due_date']

    def __str__(self):
        return f"{self.course.code} - {self.title}"

    @property
    def is_overdue(self):
        """Check if assignment is past due date."""
        return timezone.now() > self.due_date

    @property
    def submission_count(self):
        """Count of submissions for this assignment."""
        return self.submissions.count()

    @property
    def graded_count(self):
        """Count of graded submissions."""
        return self.submissions.filter(graded=True).count()


class Submission(models.Model):
    """
    Submission model representing a student's submission for an assignment.
    """
    assignment = models.ForeignKey(
        Assignment,
        on_delete=models.CASCADE,
        related_name='submissions',
        help_text="Assignment being submitted"
    )
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='submissions',
        limit_choices_to={'role': 'STUDENT'},
        help_text="Student making the submission"
    )
    submission_text = models.TextField(
        blank=True,
        help_text="Text submission content"
    )
    attachment = models.FileField(
        upload_to='submission_files/',
        blank=True,
        null=True,
        help_text="Submitted file"
    )
    submitted_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Grading
    graded = models.BooleanField(default=False, help_text="Has been graded")
    score = models.PositiveIntegerField(
        blank=True,
        null=True,
        help_text="Points earned"
    )
    feedback = models.TextField(
        blank=True,
        help_text="Instructor feedback"
    )
    graded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='graded_submissions',
        help_text="Instructor who graded this submission"
    )
    graded_at = models.DateTimeField(
        blank=True,
        null=True,
        help_text="When submission was graded"
    )

    class Meta:
        verbose_name = 'Submission'
        verbose_name_plural = 'Submissions'
        ordering = ['-submitted_at']
        unique_together = ['assignment', 'student']

    def __str__(self):
        return f"{self.student.username} - {self.assignment.title}"

    @property
    def is_late(self):
        """Check if submission was submitted after due date."""
        return self.submitted_at > self.assignment.due_date

    @property
    def percentage(self):
        """Calculate percentage score."""
        if self.graded and self.score is not None:
            return round((self.score / self.assignment.total_points) * 100, 2)
        return None


class Quiz(models.Model):
    """
    Quiz model for auto-graded assessments.
    Links to an Assignment with type='QUIZ'.
    """
    assignment = models.OneToOneField(
        Assignment,
        on_delete=models.CASCADE,
        related_name='quiz',
        limit_choices_to={'assignment_type': 'QUIZ'},
        help_text="Assignment this quiz is associated with"
    )
    time_limit = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Time limit in minutes (optional)"
    )
    allow_multiple_attempts = models.BooleanField(
        default=False,
        help_text="Allow students to retake the quiz"
    )
    max_attempts = models.PositiveIntegerField(
        default=1,
        help_text="Maximum number of attempts allowed"
    )
    show_correct_answers = models.BooleanField(
        default=True,
        help_text="Show correct answers after submission"
    )
    randomize_questions = models.BooleanField(
        default=False,
        help_text="Randomize question order for each student"
    )
    pass_percentage = models.PositiveIntegerField(
        default=60,
        help_text="Percentage required to pass"
    )

    class Meta:
        verbose_name = 'Quiz'
        verbose_name_plural = 'Quizzes'

    def __str__(self):
        return f"Quiz: {self.assignment.title}"

    @property
    def question_count(self):
        """Count of questions in this quiz."""
        return self.questions.count()

    @property
    def total_points(self):
        """Calculate total points from all questions."""
        return sum(q.points for q in self.questions.all())


class Question(models.Model):
    """
    Question model for quiz questions.
    Supports multiple choice, true/false, and short answer.
    """
    class QuestionType(models.TextChoices):
        MULTIPLE_CHOICE = 'MULTIPLE_CHOICE', 'Multiple Choice'
        TRUE_FALSE = 'TRUE_FALSE', 'True/False'
        SHORT_ANSWER = 'SHORT_ANSWER', 'Short Answer'

    quiz = models.ForeignKey(
        Quiz,
        on_delete=models.CASCADE,
        related_name='questions',
        help_text="Quiz this question belongs to"
    )
    question_text = models.TextField(help_text="The question text")
    question_type = models.CharField(
        max_length=20,
        choices=QuestionType.choices,
        default=QuestionType.MULTIPLE_CHOICE,
        help_text="Type of question"
    )
    points = models.PositiveIntegerField(
        default=1,
        help_text="Points awarded for correct answer"
    )
    order = models.PositiveIntegerField(
        default=0,
        help_text="Display order (lower numbers first)"
    )
    explanation = models.TextField(
        blank=True,
        help_text="Explanation shown after answering (optional)"
    )

    class Meta:
        verbose_name = 'Question'
        verbose_name_plural = 'Questions'
        ordering = ['order', 'id']

    def __str__(self):
        return f"{self.quiz.assignment.title} - Q{self.order}: {self.question_text[:50]}"

    def get_correct_answer(self):
        """Get the correct answer for this question."""
        if self.question_type == self.QuestionType.MULTIPLE_CHOICE:
            return self.choices.filter(is_correct=True).first()
        elif self.question_type == self.QuestionType.TRUE_FALSE:
            return self.choices.filter(is_correct=True).first()
        elif self.question_type == self.QuestionType.SHORT_ANSWER:
            # For short answer, correct_answer is stored in the first choice
            return self.choices.first()
        return None

    def check_answer(self, answer_text):
        """
        Check if an answer is correct.

        Args:
            answer_text: The student's answer

        Returns:
            bool: True if answer is correct
        """
        if self.question_type in [self.QuestionType.MULTIPLE_CHOICE, self.QuestionType.TRUE_FALSE]:
            try:
                choice = self.choices.get(choice_text=answer_text)
                return choice.is_correct
            except QuestionChoice.DoesNotExist:
                return False
        elif self.question_type == self.QuestionType.SHORT_ANSWER:
            # Case-insensitive comparison, strip whitespace
            correct = self.get_correct_answer()
            if correct:
                return answer_text.strip().lower() == correct.choice_text.strip().lower()
        return False


class QuestionChoice(models.Model):
    """
    Choice model for multiple choice and true/false questions.
    For short answer questions, stores the correct answer.
    """
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name='choices',
        help_text="Question this choice belongs to"
    )
    choice_text = models.TextField(help_text="Choice text or correct answer for short answer")
    is_correct = models.BooleanField(
        default=False,
        help_text="Is this the correct answer?"
    )
    order = models.PositiveIntegerField(
        default=0,
        help_text="Display order for choices"
    )

    class Meta:
        verbose_name = 'Question Choice'
        verbose_name_plural = 'Question Choices'
        ordering = ['order', 'id']

    def __str__(self):
        return f"{self.question.question_text[:30]} - {self.choice_text[:50]}"


class QuizAttempt(models.Model):
    """
    QuizAttempt model tracks a student's attempt at a quiz.
    Supports multiple attempts and auto-grading.
    """
    quiz = models.ForeignKey(
        Quiz,
        on_delete=models.CASCADE,
        related_name='attempts',
        help_text="Quiz being attempted"
    )
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='quiz_attempts',
        help_text="Student taking the quiz"
    )
    attempt_number = models.PositiveIntegerField(
        default=1,
        help_text="Which attempt number (1, 2, 3...)"
    )
    started_at = models.DateTimeField(auto_now_add=True)
    submitted_at = models.DateTimeField(null=True, blank=True)
    score = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Total points earned (auto-calculated)"
    )
    total_points = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Total possible points (auto-calculated)"
    )
    passed = models.BooleanField(
        default=False,
        help_text="Did student pass based on pass_percentage?"
    )

    class Meta:
        verbose_name = 'Quiz Attempt'
        verbose_name_plural = 'Quiz Attempts'
        ordering = ['-started_at']
        unique_together = ['quiz', 'student', 'attempt_number']

    def __str__(self):
        return f"{self.student.username} - {self.quiz.assignment.title} (Attempt {self.attempt_number})"

    @property
    def percentage(self):
        """Calculate percentage score."""
        if self.score is not None and self.total_points:
            return round((self.score / self.total_points) * 100, 2)
        return None

    @property
    def is_complete(self):
        """Check if quiz attempt has been submitted."""
        return self.submitted_at is not None

    def grade_quiz(self):
        """
        Auto-grade the quiz by checking all responses.
        Updates score, total_points, and passed status.
        """
        total_score = 0
        total_possible = 0

        for response in self.responses.all():
            question = response.question
            total_possible += question.points

            if question.check_answer(response.answer_text):
                response.is_correct = True
                response.points_earned = question.points
                total_score += question.points
            else:
                response.is_correct = False
                response.points_earned = 0

            response.save()

        # Update attempt score
        self.score = total_score
        self.total_points = total_possible
        self.submitted_at = timezone.now()

        # Check if passed
        if total_possible > 0:
            percentage = (total_score / total_possible) * 100
            self.passed = percentage >= self.quiz.pass_percentage

        self.save()

        # Create a corresponding Submission for gradebook integration
        self._create_submission()

    def _create_submission(self):
        """Create or update a Submission record for this quiz attempt."""
        submission, created = Submission.objects.update_or_create(
            assignment=self.quiz.assignment,
            student=self.student,
            defaults={
                'graded': True,
                'score': self.score,
                'feedback': f'Auto-graded quiz. Attempt {self.attempt_number} of {self.quiz.max_attempts}. {"Passed" if self.passed else "Failed"}.',
                'graded_at': timezone.now(),
            }
        )
        return submission


class QuizResponse(models.Model):
    """
    QuizResponse model tracks a student's response to a specific question.
    """
    attempt = models.ForeignKey(
        QuizAttempt,
        on_delete=models.CASCADE,
        related_name='responses',
        help_text="Quiz attempt this response belongs to"
    )
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name='responses',
        help_text="Question being answered"
    )
    answer_text = models.TextField(help_text="Student's answer")
    is_correct = models.BooleanField(
        null=True,
        blank=True,
        help_text="Is the answer correct? (set during grading)"
    )
    points_earned = models.PositiveIntegerField(
        default=0,
        help_text="Points earned for this question"
    )
    answered_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Quiz Response'
        verbose_name_plural = 'Quiz Responses'
        ordering = ['question__order']
        unique_together = ['attempt', 'question']

    def __str__(self):
        return f"{self.attempt.student.username} - Q{self.question.order}"
