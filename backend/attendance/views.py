from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Classroom, Student, Attendance, Houses, AttendanceTypes, PushSubscription, NotificationLog
from .serializers import ClassroomSerializer, StudentSerializer,StudentAPISerializer, AttendanceSerializer, HouseSerializer, PushSubscriptionSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q
from .models import Attendance, Student
from .serializers import AttendanceSerializer
from datetime import datetime
from rest_framework.parsers import JSONParser
from django.db.models import OuterRef, Subquery
from accounts.permisions import IsAdminUser, isCron
from pywebpush import webpush, WebPushException
import json, os
from django.utils import timezone
# import logging
from core.settings import logger
# logger = logging.getLogger(__name__)

# logger.setLevel(logging.INFO)

# # Create a handler for logging to the console
# console_handler = logging.StreamHandler()
# console_handler.setLevel(logging.INFO)

# # Create a formatter for the console handler
# console_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
# console_handler.setFormatter(console_formatter)

# # Add the console handler to the logger
# logger.addHandler(console_handler)
class ClassroomViewSet(viewsets.ModelViewSet):
    queryset = Classroom.objects.all()
    serializer_class = ClassroomSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'id'

    @action(detail=True, methods=['get'], url_path='students')
    def students(self, request, id=None):
        classroom = self.get_object()
        branch_id = request.user.branch_id
        students = Student.objects.filter(classroom=classroom, branch_id=branch_id)
        serializer = StudentSerializer(students, many=True)
        return Response(serializer.data)

class StudentViewSet(viewsets.ModelViewSet):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    permission_classes = [IsAuthenticated]

class AttendanceViewSet(viewsets.ModelViewSet):
    queryset = Attendance.objects.all()
    serializer_class = AttendanceSerializer
    permission_classes = [IsAuthenticated]

    # Custom action to get attendance for a class on a specific date
    @action(detail=False, methods=['get'], url_path='by_class_date')
    def by_class_date(self, request):
        class_id = request.query_params.get('class_id')
        date = request.query_params.get('date')
        if not class_id or not date:
            return Response({'detail': 'class_id and date are required.'}, status=400)
        students = Student.objects.filter(classroom_id=class_id)
        attendance = Attendance.objects.filter(student__in=students, date=date)
        serializer = AttendanceSerializer(attendance, many=True)
        return Response(serializer.data)


class HouseViewSet(viewsets.ModelViewSet):
    queryset = Houses.objects.all()
    serializer_class = HouseSerializer
    lookup_field = 'id'

    @action(detail=True, methods=['get'], url_path='students')
    def students(self, request, id=None):
        house = self.get_object()
        branch_id = request.user.branch_id
        students = Student.objects.filter(house=house, branch_id=branch_id)
        serializer = StudentSerializer(students, many=True)
        return Response(serializer.data)



class AttendanceAPIView(APIView):
    """
    GET: Before marking, fetch attendance for a classroom/house, date, and attendance type (att_type).
    POST: Create or update attendance records for multiple students for a given date and att_type.
    """
    parser_classes = [JSONParser]
    permission_classes = [IsAuthenticated]

    # Map att_type query param values to model field names
    ATT_TYPE_FIELD_MAP = {
        'morning': 'morning_attendance',
        'evening_att': 'evening_class_attendance',
        'morning_pt': 'morning_pt_attendance',
        'games': 'games_attendance',
        'night_dorm': 'night_dorm_attendance',
    }

    def get(self, request, *args, **kwargs):
        classroom_id = request.query_params.get('classroom')
        att_type = request.query_params.get('att_type', 'morning')
        date_str = request.query_params.get('date')
        house_id = request.query_params.get('house')
        branch_id = request.user.branch_id
        # branch_id = 1
        print("Branch ID from user context:", branch_id)
        print("Received parameters:", classroom_id, att_type, date_str)
        # Validate parameters
        if not (classroom_id or house_id )or not date_str:
            return Response({"detail": "classroom and date query parameters are required."},
                            status=status.HTTP_400_BAD_REQUEST)
        
        field_name = self.ATT_TYPE_FIELD_MAP.get(att_type)
        if not field_name:
            return Response({"detail": f"Invalid att_type: {att_type}"},
                            status=status.HTTP_400_BAD_REQUEST)
        
        try:
            query_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            return Response({"detail": "Invalid date format. Use YYYY-MM-DD."},
                            status=status.HTTP_400_BAD_REQUEST)

        # Get students of this classroom for mapping convenience
        if house_id:
            students = Student.objects.filter(house_id=house_id,branch_id=branch_id)
        elif classroom_id:
            students = Student.objects.filter(classroom_id=classroom_id, branch_id=branch_id)

        # Fetch attendance for those students and date
        attendance_qs = Attendance.objects.filter(student__in=students, date=query_date)

        # Build response list with student id and the attendance status for the requested att_type field
        response_data = []

        # Build a map student_id -> attendance object for quicker lookup
        att_map = {att.student_id: att for att in attendance_qs}

        for student in students:
            att_obj = att_map.get(student.id)
            status_value = getattr(att_obj, field_name) if att_obj else None
            # If no attendance record found, send null or you can default to 'present' if you want in frontend
            response_data.append({
                'student': student.id,
                'student_name': student.name,
                'status': status_value,
            })

        return Response(response_data, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        data = request.data
        if not isinstance(data, list):
            return Response({"detail": "Expected a list of attendance records."},
                            status=status.HTTP_400_BAD_REQUEST)
        
        errors = []
        successes = []
        for index, record in enumerate(data):
            student_id = record.get('student')
            date_str = record.get('date')
            status_value = record.get('status')
            att_type = record.get('att_type')

            if not all([student_id, date_str, status_value]):
                errors.append({"index": index, "detail": "student, date, and status are required"})
                continue
            
            field_name = self.ATT_TYPE_FIELD_MAP.get(att_type)
            if not field_name:
                errors.append({"index": index, "detail": f"Invalid att_type: {att_type}"})
                continue
            
            # if status_value not in dict(AttendanceTypes).keys():
            #     errors.append({"index": index, "detail": f"Invalid status value: {status_value}"})
            #     continue

            try:
                att_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            except ValueError:
                errors.append({"index": index, "detail": "Invalid date format. Use YYYY-MM-DD."})
                continue

            try:
                student = Student.objects.get(pk=student_id)
            except Student.DoesNotExist:
                errors.append({"index": index, "detail": f"Student id {student_id} not found"})
                continue

            attendance_obj, created = Attendance.objects.get_or_create(
                student=student,
                date=att_date,
                defaults={
                    field_name: status_value,
                })

            setattr(attendance_obj, field_name, status_value)
            try:
                attendance_obj.save()
                successes.append({"index": index, "detail": f"Attendance saved for student {student_id}"})
            except Exception as e:
                errors.append({"index": index, "detail": f"DB error: {str(e)}"})
        
        response_status = status.HTTP_200_OK if not errors else status.HTTP_207_MULTI_STATUS
        return Response({"successes": successes, "errors": errors}, status=response_status)
    


class DashboardAPIView(APIView):
    """
    GET: Fetch dashboard data for a branch.
    """
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request, *args, **kwargs):
        branch_id = request.user.branch_id
        # branch_id = 1
        date = request.query_params.get('date')
        
        
        students = Student.objects.filter(branch_id=branch_id)
        total_students = students.count()   
        # Fetch attendance for those students and date
        attendance_qs = Attendance.objects.filter(student__in=students, date=date)
        if students.count() != attendance_qs.count() and date > '2025-08-01'  :

            attendance_missed = students.count() - attendance_qs.count()
            # add attendance entry for missed students
            # bulk create attendance entries for students who missed marking
            print(f"Adding attendance for {attendance_missed} students who missed marking on {date}")
            # Create attendance entries for students who missed marking
            Attendance.objects.bulk_create([
                Attendance(student=student, date=date)
                for student in students if not attendance_qs.filter(student=student, date=date).exists()
            ])
            
        attendance_fields = [
            'morning_attendance',
            'evening_class_attendance',
            'morning_pt_attendance',
            'games_attendance',
            'night_dorm_attendance'
        ]

        attendance_types = {
            'present': AttendanceTypes.PRESENT,
            'absent': AttendanceTypes.ABSENT,
            'leave': AttendanceTypes.LEAVE,
            'on_duty': AttendanceTypes.ON_DUTY,
            'leave_sw': AttendanceTypes.LEAVE_SW,
            'NOT_MARKED': AttendanceTypes.NOT_MARKED,
        }

        
        att_dict = {}

        not_marked_count = attendance_qs.filter(morning_attendance='NOT_MARKED').count()
        print("Not Marked Count: ", not_marked_count)
        for field in attendance_fields:
            # Initialize counts for each attendance type
            attendance_counts = {}
            for label, att_type in attendance_types.items():
                key = f"{field}_{label}"
                attendance_counts[key] = attendance_qs.filter(**{field: label}).count()
            att_dict[field] = attendance_counts
        # Prepare the response data
        response_data = {
            'total_students': total_students,
            'attendance_counts': att_dict,
            'date': date,
            'branch_id': branch_id
        }
        return Response(response_data, status=status.HTTP_200_OK)
        
class AllStudentAttendanceAPIView(APIView):
    """
    GET: Fetch attendance for all students with filtering, searching, and sorting.
    """
    permission_classes = [IsAuthenticated, IsAdminUser]
    ATT_TYPE_FIELD_MAP = {
        'morning': 'morning_attendance',
        'evening_att': 'evening_class_attendance',
        'morning_pt': 'morning_pt_attendance',
        'games': 'games_attendance',
        'night_dorm': 'night_dorm_attendance',
    }
    def get(self, request, *args, **kwargs):
        date = request.query_params.get('date')
        attendance_type = request.query_params.get('attendance_type', 'morning')
        status_value = request.query_params.get('status_value', 'present')
        branch_id = request.user.branch_id
        print("date: ",date)
        if not date:
            return Response({"detail": "date query parameter is required."}, status=status.HTTP_400_BAD_REQUEST)

        field_name = self.ATT_TYPE_FIELD_MAP.get(attendance_type)

        search_query = request.query_params.get('search', '').strip()
        sort_field = request.query_params.get('sort_field', 'name')
        sort_order = request.query_params.get('sort_order', 'asc')

        # Build base queryset with JOIN to attendance
        students = Student.objects.filter(branch_id=branch_id)
        
        attendance = Attendance.objects.filter(
                Q(student__in=students) &
                Q(date=date)&
                Q(**{field_name: status_value})
            ).values('student_id')
        
        students = students.filter(id__in=attendance)
        if search_query:
            students = students.filter(Q(name__icontains=search_query) | Q(id__icontains=search_query))
        valid_sort_fields = ['name','id']
        if sort_field in valid_sort_fields:
            ordering = sort_field
            if sort_order == 'desc':
                ordering = f'-{ordering}'
            students = students.order_by(ordering)

        result = students.values('id', 'name', 'classroom__name', 'house__name')
        final_response = {
            'total_students': students.count(),
            'date': date,
            'branch_id': branch_id
        }
        result = list(result)
        final_response['students'] = result
        return Response(final_response, status=status.HTTP_200_OK)
        
        
class StudentAPIView(APIView):
    """
    GET: Fetch all students with optional filtering, searching, and sorting.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        search_query = request.query_params.get('search', '').strip()
        sort_field = request.query_params.get('sort_field', 'name')
        sort_order = request.query_params.get('sort_order', 'asc')
        branch_id = request.user.branch_id
        # branch_id = 1

        students = Student.objects.filter(branch_id=branch_id)

        if search_query:
            students = students.filter(Q(name__icontains=search_query) | Q(id__icontains=search_query))

        valid_sort_fields = ['name', 'id']
        if sort_field in valid_sort_fields:
            ordering = sort_field
            if sort_order == 'desc':
                ordering = f'-{ordering}'
            students = students.order_by(ordering)

        result = students.values('id', 'name', 'roll_number', 'classroom__name', 'house__name')
        final_response = {
            'total_students': students.count(),
            'branch_id': branch_id,
            'students': list(result)
        }
        return Response(final_response, status=status.HTTP_200_OK)
    
    def post(self, request, *args, **kwargs):
        data = request.data
        branch_id = request.user.branch_id
        logger.info("POST called by user: %s", request.user)
        logger.info("Branch ID detected: %s", request.user.branch_id)
        data['branch'] = branch_id if branch_id else 1
        logger.info("Student recieved %s",data)
        # print("Data received for student creation:", data)
        serializer = StudentAPISerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            # serializer.save(branch_id=1)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def patch(self, request, student_id, *args, **kwargs):
        branch_id = request.user.branch_id
        # branch_id = 1
        try:
            student = Student.objects.get(id=student_id, branch_id=branch_id)
        except Student.DoesNotExist:
            return Response({"detail": "Student not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = StudentAPISerializer(student, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, student_id, *args, **kwargs):
        try:
            student = Student.objects.get(id=student_id, branch_id=request.user.branch_id)
            student.delete()
            return Response({"detail": "Student deleted successfully."}, status=status.HTTP_204_NO_CONTENT)
        except Student.DoesNotExist:
            return Response({"detail": "Student not found."}, status=status.HTTP_404_NOT_FOUND)


class BulkAddStudentsAPIView(APIView):
    """
    POST: Bulk add students to a classroom.
    """
    # permission_classes = [IsAuthenticated]

    # def post(self, request, *args, **kwargs):
    #     data = request.data
    #     branch_id = 1
        
    #     students_data = data.get('students', [])
    #     if not isinstance(students_data, list) or not students_data:
    #         return Response({"detail": "students must be a non-empty list."}, status=status.HTTP_400_BAD_REQUEST)

    #     for student in students_data:
    #         student['branch'] = branch_id  # Assuming branch_id is 1 for simplicity
    #     print("Bulk adding students:", students_data)
    #     serializer = StudentSerializer(data=students_data, many=True)
        # try:
        #     serializer.is_valid(raise_exception=True)
        #     serializer.save()
        # except Exception as e:
        #     return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        # # if serializer.is_valid():
        # #     serializer.save()
        # return Response(serializer.data, status=status.HTTP_201_CREATED)
        # # return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    def post(self, request):
        students_data = request.data.get("students", [])
        branch_id = request.user.branch_id
        # branch_id = 1
        if not students_data:
            return Response({"detail": "No students data provided."}, status=status.HTTP_400_BAD_REQUEST)

        # Collect all roll_number-classroom pairs
        unique_keys = set((stu['roll_number'], stu['classroom_id']) for stu in students_data)
        existing_students = Student.objects.filter(
            roll_number__in=[r for r, _ in unique_keys],
            classroom_id__in=[c for _, c in unique_keys],
            branch_id=branch_id
        )

        # Map (roll_number, classroom) -> Student instance
        existing_map = {
            (stu.roll_number, stu.classroom_id): stu for stu in existing_students
        }

        to_create = []
        to_update = []

        for stu_data in students_data:
            # Add branch_id to each student data
            stu_data['branch_id'] = branch_id
            key = (stu_data['roll_number'], stu_data['classroom_id'])
            if key in existing_map:
                student = existing_map[key]
                for attr, value in stu_data.items():
                    setattr(student, attr, value)
                to_update.append(student)
            else:
                to_create.append(Student(**stu_data))

        # Perform bulk operations
        if to_create:
            Student.objects.bulk_create(to_create)
        if to_update:
            Student.objects.bulk_update(to_update, fields=['name', 'house'])

        return Response({
            "created": len(to_create),
            "updated": len(to_update)
        }, status=status.HTTP_200_OK)


class SavePushSubscriptionAPIView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [JSONParser]

    def post(self, request, *args, **kwargs):
        payload = request.data
        # { endpoint, keys: { p256dh, auth } }
        endpoint = payload.get('endpoint')
        keys = payload.get('keys') or {}
        p256dh = payload.get('p256dh') or keys.get('p256dh')
        auth = payload.get('auth') or keys.get('auth')
        if not endpoint or not p256dh or not auth:
            return Response({"detail": "Invalid subscription payload"}, status=status.HTTP_400_BAD_REQUEST)
        sub, _ = PushSubscription.objects.update_or_create(
            endpoint=endpoint,
            defaults={
                'user_id': request.user.id,
                'branch_id': request.user.branch_id,
                'p256dh': p256dh,
                'auth': auth,
            }
        )
        return Response({"ok": True}, status=status.HTTP_201_CREATED)


class UnsubscribePushAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]
    parser_classes = [JSONParser]

    def post(self, request, *args, **kwargs):
        payload = request.data or {}
        endpoint = payload.get('endpoint')
        keys = payload.get('keys') or {}
        p256dh = payload.get('p256dh') or keys.get('p256dh')
        auth = payload.get('auth') or keys.get('auth')
        delete_all = bool(payload.get('all'))

        qs = PushSubscription.objects.filter(user_id=request.user.id)
        if endpoint:
            qs = qs.filter(endpoint=endpoint)
        elif p256dh and auth:
            qs = qs.filter(p256dh=p256dh, auth=auth)
        elif delete_all:
            pass
        else:
            return Response({"detail": "Provide endpoint or keys {p256dh, auth} or all=true"}, status=status.HTTP_400_BAD_REQUEST)

        deleted_count, _ = qs.delete()
        return Response({"ok": True, "deleted": deleted_count})


class TriggerUnmarkedPushAPIView(APIView):
    permission_classes = [isCron]
    parser_classes = [JSONParser]
    ATT_TYPE_FIELD_MAP = AttendanceAPIView.ATT_TYPE_FIELD_MAP

    def post(self, request, *args, **kwargs):
        date_str = request.data.get('date')
        att_type = request.data.get('attendance_type', 'morning')
        scope = request.data.get('scope')
        scope_id = request.data.get('scope_id')
        scope_only = request.data.get('scope_only')  # optional: 'class' | 'house'

        if att_type not in self.ATT_TYPE_FIELD_MAP:
            return Response({"detail": "valid attendance_type is required"}, status=400)

        if date_str:
            try:
                day = datetime.strptime(date_str, '%Y-%m-%d').date()
            except ValueError:
                return Response({"detail": "Invalid date format"}, status=400)
        else:
            day = timezone.localdate()

        field_name = self.ATT_TYPE_FIELD_MAP[att_type]
        branch_id = request.user.branch_id

        scopes = []
        if scope == 'class' and scope_id:
            scopes = [('class', int(scope_id))]
        elif scope == 'house' and scope_id:
            scopes = [('house', int(scope_id))]
        else:
            class_ids = list(Classroom.objects.values_list('id', flat=True))
            house_ids = list(Houses.objects.values_list('id', flat=True))
            if scope_only == 'class':
                scopes = [('class', cid) for cid in class_ids]
            elif scope_only == 'house':
                scopes = [('house', hid) for hid in house_ids]
            else:
                scopes = [('class', cid) for cid in class_ids] + [('house', hid) for hid in house_ids]

        notified = []
        for scope_type, sid in scopes:
            if NotificationLog.objects.filter(branch_id=branch_id, date=day, session_key=att_type, scope_type=scope_type, scope_id=sid).exists():
                continue

            if scope_type == 'class':
                students = Student.objects.filter(branch_id=branch_id, classroom_id=sid)
            else:
                students = Student.objects.filter(branch_id=branch_id, house_id=sid)

            has_unmarked = Attendance.objects.filter(
                student__in=students,
                date=day,
                **{field_name: 'NOT_MARKED'}
            ).exists()
            if has_unmarked:
                if scope_type == 'class':
                    class_name = Classroom.objects.filter(id=sid).values_list('name', flat=True).first() or str(sid)
                    scope_label = f"{class_name}"
                elif scope_type == 'house':
                    house_obj = Houses.objects.filter(id=sid).first()
                    house_name = house_obj.get_name_display() if house_obj else str(sid)
                    scope_label = f"{house_name}"

                self._send_push_to_branch(
                    branch_id,
                    title=f"Notice: {att_type.replace('_', ' ')} attendance",
                    body=f"Unmarked entries detected for {day} in {scope_label}.",
                )
                NotificationLog.objects.create(branch_id=branch_id, date=day, session_key=att_type, scope_type=scope_type, scope_id=sid)
                notified.append({"scope": scope_type, "id": sid})

        return Response({"ok": True, "notified": notified})

    @staticmethod
    def _send_push_to_branch(branch_id: int, title: str, body: str) -> None:

        # Notify only admins in this branch
        subs = PushSubscription.objects.filter(branch_id=branch_id, user__role='admin', user__is_active=True)
        vapid_private = os.environ.get('VAPID_PRIVATE_KEY', 'IrPD0MjfOewL70dJrICeQLY4h_JVdJPKwC-4SbM3vA8')
        vapid_email = os.environ.get('VAPID_EMAIL', 'mailto:gautam@superadmin.com')
        if not vapid_private:
            logger.warning("VAPID_PRIVATE_KEY not set; skipping push send")
            return
        payload = json.dumps({"title": title, "body": body})
        for sub in subs:
            try:
                webpush(subscription_info=sub.as_webpush_dict(), data=payload, vapid_private_key=vapid_private, vapid_claims={"sub": vapid_email})
                logger.info("Push sent to %s", sub.endpoint)
                logger.info("Push payload: %s", payload)
                
            except WebPushException as e:
                logger.warning("Push send failed for %s: %s", sub.endpoint, str(e))
