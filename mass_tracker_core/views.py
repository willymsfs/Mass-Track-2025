from rest_framework import viewsets, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from django.db import transaction
from datetime import date, timedelta
from .models import Priest, IntentionType, IntentionSource, MassIntention, PersonalMassIntention, FixedDateMassIntention, BulkMassIntention, MassCelebration, DailyStatus
from .serializers import PriestSerializer, IntentionTypeSerializer, IntentionSourceSerializer, MassIntentionSerializer, PersonalMassIntentionSerializer, FixedDateMassIntentionSerializer, BulkMassIntentionSerializer, MassCelebrationSerializer, DailyStatusSerializer
import openpyxl

# Authentication views
@api_view(["POST"])
@permission_classes([AllowAny])
def register(request):
    serializer = PriestSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        token, created = Token.objects.get_or_create(user=user)
        return Response(
            {
                "user": PriestSerializer(user).data,
                "token": token.key,
            },
            status=status.HTTP_201_CREATED,
        )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
@permission_classes([AllowAny])
def login(request):
    email = request.data.get("email")
    password = request.data.get("password")

    if email and password:
        user = authenticate(username=email, password=password)
        if user:
            token, created = Token.objects.get_or_create(user=user)
            return Response(
                {
                    "user": PriestSerializer(user).data,
                    "token": token.key,
                },
                status=status.HTTP_200_OK,
            )

    return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)


# Dashboard view
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def dashboard(request):
    priest = request.user
    today = date.today()

    # Get today's status
    daily_status = DailyStatus.objects.filter(priest=priest, date=today).first()

    # Get personal mass progress for current month
    personal_masses = PersonalMassIntention.objects.filter(
        mass_intention__priest=priest,
        month=today.month,
        year=today.year,
    )
    personal_masses_celebrated_count = personal_masses.filter(celebrated_date__isnull=False).count()

    # Get active bulk masses
    bulk_masses = BulkMassIntention.objects.filter(
        mass_intention__priest=priest,
        remaining_masses__gt=0
    ).select_related("mass_intention")

    # Calculate estimated end date for bulk masses
    for bulk in bulk_masses:
        if not bulk.is_paused and bulk.remaining_masses > 0:
            # Simple estimation: 1 mass per day
            bulk.estimated_end_date = today + timedelta(days=bulk.remaining_masses)
        else:
            bulk.estimated_end_date = None

    # Get upcoming fixed date masses
    fixed_date_masses = FixedDateMassIntention.objects.filter(
        mass_intention__priest=priest,
        is_celebrated=False,
        original_date__gte=today
    ).order_by("original_date")[:5].select_related("mass_intention")

    # Alerts
    alerts = []
    if personal_masses_celebrated_count < 3:
        alerts.append(f"You have {3 - personal_masses_celebrated_count} personal masses pending for this month.")
    
    for bulk in bulk_masses:
        if bulk.remaining_masses <= 10 and bulk.remaining_masses > 0:
            alerts.append(f"Bulk mass \'{bulk.mass_intention.title}\' is about to complete ({bulk.remaining_masses} left).")
    
    for fixed_mass in fixed_date_masses:
        if fixed_mass.original_date == today:
            alerts.append(f"Fixed-date mass \'{fixed_mass.mass_intention.title}\' is scheduled for today!")
        elif fixed_mass.original_date == today + timedelta(days=1):
            alerts.append(f"Fixed-date mass \'{fixed_mass.mass_intention.title}\' is scheduled for tomorrow.")

    return Response({
        "today_status": DailyStatusSerializer(daily_status).data if daily_status else None,
        "personal_masses_celebrated_count": personal_masses_celebrated_count,
        "personal_masses_details": PersonalMassIntentionSerializer(personal_masses, many=True).data,
        "bulk_masses": BulkMassIntentionSerializer(bulk_masses, many=True).data,
        "upcoming_fixed_masses": FixedDateMassIntentionSerializer(fixed_date_masses, many=True).data,
        "alerts": alerts,
    })


# Mass celebration endpoint
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def celebrate_mass(request):
    priest = request.user
    mass_intention_id = request.data.get("mass_intention_id")
    celebration_date = request.data.get("celebration_date", date.today())
    notes = request.data.get("notes", "")

    try:
        with transaction.atomic():
            mass_intention = MassIntention.objects.get(id=mass_intention_id, priest=priest)

            # Create mass celebration record
            mass_celebration = MassCelebration.objects.create(
                priest=priest,
                mass_intention=mass_intention,
                celebration_date=celebration_date,
                notes=notes,
            )

            # Update daily status
            daily_status, created = DailyStatus.objects.get_or_create(
                priest=priest,
                date=celebration_date,
                defaults={"celebrated_mass": True},
            )
            if not created:
                daily_status.celebrated_mass = True
                daily_status.save()

            # Handle specific intention types
            if mass_intention.intention_type.name == "Personal":
                personal_intention = PersonalMassIntention.objects.get(mass_intention=mass_intention)
                personal_intention.celebrated_date = celebration_date
                personal_intention.save()
                # If a personal mass is celebrated, pause any active bulk masses
                BulkMassIntention.objects.filter(mass_intention__priest=priest, is_paused=False).update(is_paused=True)

            elif mass_intention.intention_type.name == "Fixed-Date":
                fixed_intention = FixedDateMassIntention.objects.get(mass_intention=mass_intention)
                fixed_intention.is_celebrated = True
                fixed_intention.save()
                # If a fixed-date mass is celebrated, pause any active bulk masses
                BulkMassIntention.objects.filter(mass_intention__priest=priest, is_paused=False).update(is_paused=True)

            elif mass_intention.intention_type.name == "Bulk":
                bulk_intention = BulkMassIntention.objects.get(mass_intention=mass_intention)
                if bulk_intention.remaining_masses > 0:
                    bulk_intention.remaining_masses -= 1
                    bulk_intention.last_celebrated_date = celebration_date
                    bulk_intention.is_paused = False # Ensure bulk is not paused if celebrated
                    bulk_intention.save()

            return Response(
                {
                    "message": "Mass celebrated successfully",
                    "mass_celebration": MassCelebrationSerializer(mass_celebration).data,
                },
                status=status.HTTP_201_CREATED,
            )

    except MassIntention.DoesNotExist:
        return Response({"error": "Mass intention not found"}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def toggle_bulk_mass_pause(request):
    bulk_mass_intention_id = request.data.get("bulk_mass_intention_id")
    priest = request.user

    try:
        bulk_intention = BulkMassIntention.objects.get(mass_intention__id=bulk_mass_intention_id, mass_intention__priest=priest)
        bulk_intention.is_paused = not bulk_intention.is_paused
        bulk_intention.save()
        return Response({"message": "Bulk mass pause status toggled successfully", "is_paused": bulk_intention.is_paused}, status=status.HTTP_200_OK)
    except BulkMassIntention.DoesNotExist:
        return Response({"error": "Bulk mass intention not found"}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def import_excel_data(request):
    priest = request.user
    excel_file = request.FILES.get("file")
    start_year = int(request.data.get("start_year", 2000))
    end_year = int(request.data.get("end_year", date.today().year))

    if not excel_file:
        return Response({"error": "No Excel file provided"}, status=status.HTTP_400_BAD_REQUEST)

    if not excel_file.name.endswith((".xlsx", ".xls")):
        return Response({"error": "Invalid file format. Only .xlsx and .xls are supported."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        workbook = openpyxl.load_workbook(excel_file)
        sheet = workbook.active
        
        # Assuming the Excel sheet has columns like: Date, Intention, Source, Type, Notes, Bulk_Remaining, Bulk_Total
        # You'll need to adjust column indices based on your actual Excel file structure
        
        # For simplicity, let's assume columns are in order: A=Date, B=Intention, C=Source, D=Type, E=Notes, F=Bulk_Remaining, G=Bulk_Total
        # You might need a more robust way to map columns, e.g., by header names

        imported_count = 0
        for row_index, row in enumerate(sheet.iter_rows(min_row=2), start=2): # Assuming first row is header
            try:
                # Extract data from row
                celebration_date_str = row[0].value # Column A
                intention_title = row[1].value # Column B
                source_name = row[2].value # Column C
                type_name = row[3].value # Column D
                notes = row[4].value # Column E
                bulk_remaining = row[5].value # Column F
                bulk_total = row[6].value # Column G

                # Data validation and conversion
                if not all([celebration_date_str, intention_title, source_name, type_name]):
                    print(f"Skipping row {row_index}: Missing required data.")
                    continue

                try:
                    celebration_date = date.fromisoformat(str(celebration_date_str)) # Assuming YYYY-MM-DD format
                except ValueError:
                    print(f"Skipping row {row_index}: Invalid date format ", celebration_date_str)
                    continue

                if not (start_year <= celebration_date.year <= end_year):
                    print(f"Skipping row {row_index}: Date {celebration_date.year} outside specified range.")
                    continue

                with transaction.atomic():
                    # Get or create IntentionType and IntentionSource
                    intention_type, _ = IntentionType.objects.get_or_create(name=type_name)
                    intention_source, _ = IntentionSource.objects.get_or_create(name=source_name)

                    # Create MassIntention
                    mass_intention = MassIntention.objects.create(
                        priest=priest,
                        intention_type=intention_type,
                        intention_source=intention_source,
                        title=intention_title,
                        description=notes # Using notes as description for simplicity
                    )

                    # Create MassCelebration
                    MassCelebration.objects.create(
                        priest=priest,
                        mass_intention=mass_intention,
                        celebration_date=celebration_date,
                        notes=notes
                    )

                    # Update DailyStatus
                    daily_status, created = DailyStatus.objects.get_or_create(
                        priest=priest,
                        date=celebration_date,
                        defaults={'celebrated_mass': True}
                    )
                    if not created:
                        daily_status.celebrated_mass = True
                        daily_status.save()

                    # Handle specific intention types for historical data
                    if type_name == 'Personal':
                        PersonalMassIntention.objects.create(
                            mass_intention=mass_intention,
                            month=celebration_date.month,
                            year=celebration_date.year,
                            celebrated_date=celebration_date
                        )
                    elif type_name == 'Fixed-Date':
                        FixedDateMassIntention.objects.create(
                            mass_intention=mass_intention,
                            original_date=celebration_date,
                            is_celebrated=True # Assuming historical fixed-date masses are celebrated
                        )
                    elif type_name == 'Bulk':
                        if bulk_total is not None and bulk_remaining is not None:
                            BulkMassIntention.objects.create(
                                mass_intention=mass_intention,
                                total_masses=bulk_total,
                                remaining_masses=bulk_remaining,
                                start_date=celebration_date,
                                last_celebrated_date=celebration_date
                            )

                    imported_count += 1

            except Exception as e:
                print(f"Error processing row {row_index}: {e}")
                # Optionally, log the error and continue or return an error response
                continue

        return Response({"message": f"Successfully imported {imported_count} mass records."}, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ViewSets for CRUD operations
class IntentionTypeViewSet(viewsets.ModelViewSet):
    queryset = IntentionType.objects.all()
    serializer_class = IntentionTypeSerializer
    permission_classes = [IsAuthenticated]


class IntentionSourceViewSet(viewsets.ModelViewSet):
    queryset = IntentionSource.objects.all()
    serializer_class = IntentionSourceSerializer
    permission_classes = [IsAuthenticated]


class MassIntentionViewSet(viewsets.ModelViewSet):
    serializer_class = MassIntentionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return MassIntention.objects.filter(priest=self.request.user)


class PersonalMassIntentionViewSet(viewsets.ModelViewSet):
    serializer_class = PersonalMassIntentionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return PersonalMassIntention.objects.filter(mass_intention__priest=self.request.user)


class FixedDateMassIntentionViewSet(viewsets.ModelViewSet):
    serializer_class = FixedDateMassIntentionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return FixedDateMassIntention.objects.filter(mass_intention__priest=self.request.user)


class BulkMassIntentionViewSet(viewsets.ModelViewSet):
    serializer_class = BulkMassIntentionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return BulkMassIntention.objects.filter(mass_intention__priest=self.request.user)


class MassCelebrationViewSet(viewsets.ModelViewSet):
    serializer_class = MassCelebrationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return MassCelebration.objects.filter(priest=self.request.user)


class DailyStatusViewSet(viewsets.ModelViewSet):
    serializer_class = DailyStatusSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return DailyStatus.objects.filter(priest=self.request.user)


