from datetime import time
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .serializers import ResultSerializer
from attendance.models import Student
from .models import Results, Exam
import time
from core.settings import logger
class ResultsAPI(APIView):
    # permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        """
        Create a new result entry for a student.
        Expects student ID, subject, score, and exam ID in the request data.
        """
        # Validate that the student exists
        student_roll = request.data.get('student_roll')
        classroom_id = request.data.get('classroom_id')
        if not student_roll:
            return Response({"error": "Student roll number is required."}, status=status.HTTP_400_BAD_REQUEST)
        student = get_object_or_404(Student, roll_number=student_roll, classroom_id=classroom_id)
        # create or update result
        request.data['student'] = student.id
        # Validate and save the result
        request.data['exam'] = request.data.get('exam')
        if not request.data.get('exam'):
            return Response({"error": "Exam ID is required."}, status=status.HTTP_400_BAD_REQUEST)      
        if not request.data.get('subject'):
            return Response({"error": "Subject is required."}, status=status.HTTP_400_BAD_REQUEST)
        if not request.data.get('score'):
            return Response({"error": "Score is required."}, status=status.HTTP_400_BAD_REQUEST)
        if not isinstance(request.data.get('score'), int):
            return Response({"error": "Score must be an integer."}, status=status.HTTP_400_BAD_REQUEST)
        if request.data.get('score') < 0:
            return Response({"error": "Score cannot be negative."}, status=status.HTTP_400_BAD_REQUEST)
        if request.data.get('score') > 100:
            return Response({"error": "Score cannot exceed 100."}, status=status.HTTP_400_BAD_REQUEST)
        # check if the result already exists

        subject=request.data.get('subject')
        existing_result = Results.objects.filter(student=student, subject=subject, exam=request.data.get('exam')).first()
        if existing_result:
            # Update existing result
            serializer = ResultSerializer(existing_result, data=request.data, partial=True)
        else:
            serializer = ResultSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class BulkResultsAPI(APIView):
    # permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        """
        Bulk create or update results for multiple students using bulk operations.
        Expects a list of results in the request data.
        """
        results_data = request.data.get('results', [])
        if not results_data:
            return Response({"error": "Results data is required."}, status=status.HTTP_400_BAD_REQUEST)
        
        # Validate all data first
        validated_data = []
        student_dict = {}

        for idx, result_data in enumerate(results_data):
            try:
                # Validate required fields
                student_roll = result_data.get('student_roll')
                classroom_id = result_data.get('classroom_id')
                subject = result_data.get('subject')
                score = result_data.get('score')
                exam_id = result_data.get('exam')
                
                if not all([student_roll, classroom_id, subject, score is not None, exam_id]):
                    return Response({
                        "error": f"Missing required fields in result {idx + 1}. Required: student_roll, classroom_id, subject, score, exam"
                    }, status=status.HTTP_400_BAD_REQUEST)
                
                # Validate score
                if not isinstance(score, int) or score < 0 or score > 100:
                    return Response({
                        "error": f"Invalid score in result {idx + 1}. Score must be an integer between 0 and 100."
                    }, status=status.HTTP_400_BAD_REQUEST)
                
                # Get student (use cache to avoid repeated queries)
                student_key = f"{student_roll}_{classroom_id}"
                if student_key not in student_dict:
                    try:
                        student = Student.objects.get(roll_number=student_roll, classroom_id=classroom_id)
                        student_dict[student_key] = student
                    except Student.DoesNotExist:
                        return Response({
                            "error": f"Student with roll number {student_roll} in classroom {classroom_id} not found."
                        }, status=status.HTTP_400_BAD_REQUEST)

                student = student_dict[student_key]

                validated_data.append({
                    'student': student,
                    'student_id': student.id,
                    'subject': subject,
                    'score': score,
                    'exam_id': exam_id,
                    'original_data': result_data
                })
                
            except Exception as e:
                return Response({
                    "error": f"Validation error in result {idx + 1}: {str(e)}"
                }, status=status.HTTP_400_BAD_REQUEST)
        
        # Get existing results for bulk operations
        student_ids = [data['student_id'] for data in validated_data]
        subjects = list(set(data['subject'] for data in validated_data))
        exam_ids = list(set(data['exam_id'] for data in validated_data))
        
        existing_results = Results.objects.filter(
            student_id__in=student_ids,
            subject__in=subjects,
            exam_id__in=exam_ids
        )
        # print("Existing results:", existing_results)
        # Create lookup dictionary for existing results
        existing_lookup = {
            (result.student_id, result.subject, result.exam_id): result
            for result in existing_results
        }
        
        # print("Existing results lookup:", existing_lookup)
        # Separate data into create and update lists
        to_create = []
        to_update = []
        
        for data in validated_data:
            key = (data['student_id'], data['subject'], data['exam_id'])
            # print("Processing data:", data, "Key:", key)
            if key in existing_lookup:
                # Update existing result
                existing_result = existing_lookup[key]
                existing_result.score = data['score']
                to_update.append(existing_result)
            else:
                # Create new result
                new_result = Results(
                    student=data['student'],
                    subject=data['subject'],
                    score=data['score'],
                    exam_id=data['exam_id']
                )
                to_create.append(new_result)
        
        # Perform bulk operations
        created_count = 0
        updated_count = 0
        
        try:
            if to_create:
                Results.objects.bulk_create(to_create, batch_size=100)
                created_count = len(to_create)
            
            if to_update:
                Results.objects.bulk_update(to_update, ['score'], batch_size=100)
                updated_count = len(to_update)
            
            return Response({
                "message": "Bulk operation completed successfully",
                "created": created_count,
                "updated": updated_count,
                "total_processed": len(validated_data)
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                "error": f"Database operation failed: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
class StudentResultsDetailAPI(APIView):
    # permission_classes = [IsAuthenticated]

    def get(self, request, student_id, *args, **kwargs):
        """
        Retrieve detailed results for a specific student and exam.
        """
        exam_id = request.query_params.get('exam_id')
        result = Results.objects.filter(student__id=student_id, exam__id=exam_id).values('student__name', 'subject', 'score', 'exam__name')
        # serializer = ResultSerializer(result)
        return Response(result)
    
class SubjectResultsAPI(APIView):
    # permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        """
        Retrieve results for a specific subject across all students of a classroom.
        """
        subject = kwargs.get('subject')
        classroom_id = kwargs.get('classroom_id')
        exam_id = request.query_params.get('exam_id')
        results = Results.objects.filter(subject=subject, student__classroom__id=classroom_id, exam__id=exam_id)
        serializer = ResultSerializer(results, many=True)
        return Response(serializer.data)
    
class ClassResultDashBoardAPI(APIView):
    # permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        """
        Retrieve results for a specific classroom with top and bottom performers across all subjects.
        """
        classroom_id = request.query_params.get('classroom_id')
        exam_id = request.query_params.get('exam_id')
        branch_id = request.query_params.get('branch_id')
        if not classroom_id:
            return Response({"error": "Classroom ID is required."}, status=status.HTTP_400_BAD_REQUEST)
        
        # Base query for classroom results
        base_query = Results.objects.filter(student__classroom_id=classroom_id, student__branch_id=branch_id)
        logger.info("base query: ", base_query)
        # Filter by exam if provided
        
        base_query = base_query.filter(exam__id=exam_id)
        
        if not base_query.exists():
            return Response({"error": "No results found for this classroom."}, status=status.HTTP_200_OK)
        
        # Get all unique subjects for this classroom
        subjects = base_query.values_list('subject', flat=True).distinct()
        
        classroom_performance = {
            'classroom_id': classroom_id,
            'exam_id': exam_id,
            'subject_performance': []
        }
        
        # for subject in subjects:
        #     subject_results = base_query.filter(subject=subject).select_related('student')
            
        #     if subject_results.exists():
        #         # Get top 5 performers (highest scores)
        #         top_performers = subject_results.order_by('-score', 'student__name')[:5]
                
        #         # Get bottom 5 performers (lowest scores)
        #         bottom_performers = subject_results.order_by('score', 'student__name')[:5]
                
        #         # Calculate subject statistics
        #         scores = list(subject_results.values_list('score', flat=True))
        #         avg_score = sum(scores) / len(scores) if scores else 0
                
        #         subject_data = {
        #             'subject': subject,
        #             'total_students': subject_results.count(),
        #             'average_score': round(avg_score, 2),
        #             'highest_score': max(scores) if scores else None,
        #             'lowest_score': min(scores) if scores else None,
        #             'top_5_performers': [
        #                 {
        #                     'student_id': performer.student.roll_number,
        #                     'student_name': performer.student.name,
        #                     'score': performer.score,
        #                     'rank': idx + 1
        #                 } for idx, performer in enumerate(top_performers)
        #             ],
        #             'bottom_5_performers': [
        #                 {
        #                     'student_id': performer.student.roll_number,
        #                     'student_name': performer.student.name,
        #                     'score': performer.score,
        #                     'rank': subject_results.count() - len(bottom_performers) + idx + 1
        #                 } for idx, performer in enumerate(bottom_performers)
        #             ]
        #         }
                
        #         classroom_performance['subject_performance'].append(subject_data)
        # Calculate classroom top and bottom performers based on overall percentage across all subjects
        from django.db.models import Avg, Count
        
        # Get students with their average scores across all subjects for this exam
        student_averages = base_query.values('student__id', 'student__name', 'student__roll_number') \
                                   .annotate(
                                       avg_score=Avg('score'),
                                       subject_count=Count('subject', distinct=True)
                                   ) \
                                   .order_by('-avg_score', 'student__name')
        
        # Filter students who have results in multiple subjects (more comprehensive evaluation)
        min_subjects_required = max(1, len(subjects) // 2)  # At least half the subjects
        qualified_students = [
            student for student in student_averages 
            if student['subject_count'] >= min_subjects_required
        ]
        
        # Get top 5 and bottom 5 overall performers
        top_class_performers = qualified_students[:5]
        # For bottom performers, get the last 5 and reverse them to show lowest first
        bottom_class_performers = qualified_students[-5:]
        bottom_class_performers.reverse()  # Reverse to show lowest scores first
        
        classroom_performance['top_class_performers'] = [
            {
                'student_id': performer['student__roll_number'],
                'student_name': performer['student__name'],
                'average_percentage': round(performer['avg_score'], 2),
                'subjects_appeared': performer['subject_count'],
                'rank': idx + 1
            } for idx, performer in enumerate(top_class_performers)
        ]

        # Calculate bottom performers with correct ranking (from lowest to highest)
        total_students = len(qualified_students)
        classroom_performance['bottom_class_performers'] = [
            {
                'student_id': performer['student__roll_number'],
                'student_name': performer['student__name'],
                'average_percentage': round(performer['avg_score'], 2),
                'subjects_appeared': performer['subject_count'],
                'rank': total_students - len(bottom_class_performers) + idx + 1
            } for idx, performer in enumerate(bottom_class_performers)
        ]
        
        # Calculate overall classroom statistics
        overall_scores = list(base_query.values_list('score', flat=True))   
        overall_avg_score = sum(overall_scores) / len(overall_scores) if overall_scores else 0
        
        classroom_performance['overall_statistics'] = {
            'total_students_with_results': len(qualified_students),
            'total_result_entries': base_query.count(),
            'subjects_covered': len(subjects),
            'average_score_all_results': round(overall_avg_score, 2),
            }
        logger.info("classroom_performance: ", classroom_performance)
        # Return the classroom performance data
        return Response(classroom_performance, status=status.HTTP_200_OK)
    
class SubjectResultsDashboardAPI(APIView):
    # permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        """
        Retrieve results for a specific subject across all students of a classroom with top 5 and bottom 5 performers.
        """
        subject = request.query_params.get('subject')
        classroom_id = request.query_params.get('classroom_id')
        exam_id = request.query_params.get('exam_id')

        if not subject or not classroom_id:
            return Response({"error": "Subject and Classroom ID are required."}, status=status.HTTP_400_BAD_REQUEST)
        
        results = Results.objects.filter(subject=subject, student__classroom__id=classroom_id)

        if exam_id:
            results = results.filter(exam__id=exam_id)

        if not results.exists():
            return Response({"error": "No results found for this subject in the specified classroom."}, status=status.HTTP_200_OK)
        
        # Get top 5 performers (highest scores)
        top_performers = results.order_by('-score', 'student__name')[:5]
        
        # Get bottom 5 performers (lowest scores)
        bottom_performers = results.order_by('score', 'student__name')[:5]
        
        # Calculate subject statistics
        scores = list(results.values_list('score', flat=True))
        avg_score = sum(scores) / len(scores) if scores else 0
        
        subject_data = {
            'subject': subject,
            'classroom_id': classroom_id,
            'exam_id': exam_id,
            'total_students': results.count(),
            'average_score': round(avg_score, 2),
            'highest_score': max(scores) if scores else None,
            'lowest_score': min(scores) if scores else None,
            'top_5_performers': [
                {
                    'student_id': performer.student.roll_number,
                    'student_name': performer.student.name,
                    'score': performer.score,
                    'rank': idx + 1
                } for idx, performer in enumerate(top_performers)
            ],
            'bottom_5_performers': [
                {
                    'student_id': performer.student.roll_number,
                    'student_name': performer.student.name,
                    'score': performer.score,
                    'rank': results.count() - len(bottom_performers) + idx + 1
                } for idx, performer in enumerate(bottom_performers)
            ]
        }
        
        return Response(subject_data, status=status.HTTP_200_OK)
        

class ListSubjectsAPI(APIView):
    # permission_classes = [IsAuthenticated]

    # Constant map of classroom_id to subject list
    subject_mappings = {
        'Primary': ['ENGLISH','MATHS','SCIENCE','SOCIAL SCIENCE', 'HINDI', 'IT'],
        'Secondary': ['ENGLISH','MATHS','PHYSICS','CHEMISTRY', 'BIOLOGY', 'IT', 'COMPUTER SCIENCE'],
    }
    def get(self, request, *args, **kwargs):
        """
        List all subjects based on class and branch.
        """

        class_type = request.query_params.get('class_type')
        if not class_type:
            return Response({"error": "Class type is required."}, status=status.HTTP_400_BAD_REQUEST)
        return Response({
            'subjects': self.subject_mappings.get(class_type, [])
        }, status=status.HTTP_200_OK)
        

class ListExamsAPI(APIView):

    # permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        """
        List all tests based on class and subject.
        """
        start_time = time.time()
        exams = Exam.objects.all().values('id', 'name')
        end_time = time.time()
        print(f"Time taken to fetch exams: {end_time - start_time} seconds")
        return Response(exams, status=status.HTTP_200_OK)
    
class StudentResultListAPIView(APIView):
    """
    GET: fetch all students of a classroom with their results for a specific subject and exam.
    Returns all students with score if exists, otherwise "NA".
    """
    # permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        subject = request.query_params.get('subject')
        classroom_id = request.query_params.get('classroom_id')
        exam_id = request.query_params.get('exam_id')

        if not subject or not classroom_id:
            return Response({"error": "Subject and Classroom ID are required."}, status=status.HTTP_400_BAD_REQUEST)

        # Check if special course filtering is needed for certain classrooms
        check_course = False
        if classroom_id and int(classroom_id) in [11, 13]:
            check_course = True
        
        # Get all students in the classroom
        students_list = Student.objects.filter(
            classroom_id=classroom_id, 
            branch_id=1
        ).order_by('roll_number', 'name')
        
        # Apply course filtering for specific subjects and classrooms
        if check_course and (subject == 'IT' or subject == 'Computer Science'):
            students_list = students_list.filter(course='PCMC')
        elif check_course and (subject == 'Biology'):
            students_list = students_list.filter(course='PCMB')

        # Get existing results for these students and subject
        results_query = Results.objects.filter(
            student__in=students_list, 
            subject=subject
        )
        
        # Filter by exam if provided
        if exam_id:
            results_query = results_query.filter(exam_id=exam_id)
        
        # Create a dictionary for quick lookup of results
        results_dict = {
            result.student_id: result.score 
            for result in results_query
        }

        # Build response with all students and their scores (or "NA")
        students_with_results = []
        for student in students_list:
            score = results_dict.get(student.id, "NA")
            
            students_with_results.append({
                'student_id': student.id,
                'roll_number': student.roll_number,
                'student_name': student.name,
                'course': getattr(student, 'course', None),
                'score': score,
                'has_result': score != "NA"
            })

        return Response({
            "subject": subject,
            "classroom_id": classroom_id,
            "exam_id": exam_id,
            "total_students": len(students_with_results),
            "students_with_results": len([s for s in students_with_results if s['has_result']]),
            "students_without_results": len([s for s in students_with_results if not s['has_result']]),
            "students": students_with_results
        }, status=status.HTTP_200_OK)
