from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login as auth_login
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Avg
from django.http import HttpResponse
import csv, io, datetime, json
from django.contrib.auth.forms import AuthenticationForm 
from .models import SleepSession, SleepGoal
from .forms import SleepSessionForm, SleepGoalForm
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
import logging

logger = logging.getLogger(__name__)

class CustomLoginView(LoginView):
    template_name = 'login.html'
    success_url = reverse_lazy('sleep:session_list')

    def form_valid(self, form):
        logger.info(f"Login successful for user: {form.get_user().username}")
        return super().form_valid(form)

    def form_invalid(self, form):
        logger.error(f"Login failed: {form.errors}")
        return super().form_invalid(form)

@login_required
def session_list(request):
    logger.info(f"Rendering session_list for user: {request.user.username}")
    return render(request, 'base.html', {'sessions': []})

# Other placeholder views...
@login_required
def goal_view(request):
    return render(request, 'base.html', {'goal': None})

@login_required
def import_csv(request):
    return render(request, 'base.html', {})

@login_required
def export_csv(request):
    return render(request, 'base.html', {})

def signup_view(request):
    return render(request, 'signup.html', {})

def get_success_url(self):
    if self.request.user.is_authenticated:
        return reverse_lazy('sleep:session_list')
    return reverse_lazy('sleep:login')
    
def login_view(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                auth_login(request, user)
                return render(request, "base.html")
            else:
                form.add_error(None, "Invalid username or password.")
    else:
        form = AuthenticationForm()
    return render(request, "login.html", {"form": form})

def signup(request):
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)
            return redirect("dashboard")
    else:
        form = SignUpForm()
    return render(request, "signup.html", {"form": form})

@login_required
def dashboard(request):
    sessions = SleepSession.objects.filter(user=request.user).order_by("-start")[:30]
    # Prepare data for charts
    chart_labels = []
    chart_hours = []
    chart_quality = []
    for s in sessions[::-1]:
        chart_labels.append(s.start.strftime("%b %d"))
        chart_hours.append(s.duration_hours)
        chart_quality.append(s.quality)

    goal_hours = None
    try:
        goal_hours = float(request.user.sleep_goal.target_hours)
    except SleepGoal.DoesNotExist:
        pass

    stats = {}
    if sessions:
        stats["avg_hours"] = round(sum(s.duration_hours for s in sessions) / len(sessions), 2)
        stats["avg_quality"] = round(sum(s.quality for s in sessions) / len(sessions), 2)
    else:
        stats["avg_hours"] = 0
        stats["avg_quality"] = 0

    return render(request, "dashboard.html", {
        "sessions": sessions,
        "chart_labels": json.dumps(chart_labels),
        "chart_hours": json.dumps(chart_hours),
        "chart_quality": json.dumps(chart_quality),
        "goal_hours": goal_hours,
        "stats": stats,
    })

@login_required
def session_list(request):
    sessions = SleepSession.objects.filter(user=request.user).order_by("-start")
    return render(request, "sessions.html", {"sessions": sessions})

@login_required
def session_create(request):
    if request.method == "POST":
        form = SleepSessionForm(request.POST)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.user = request.user
            obj.save()
            return redirect("session_list")
    else:
        form = SleepSessionForm()
    return render(request, "session_form.html", {"form": form, "title": "Log Sleep"})

@login_required
def session_edit(request, pk):
    obj = get_object_or_404(SleepSession, pk=pk, user=request.user)
    if request.method == "POST":
        form = SleepSessionForm(request.POST, instance=obj)
        if form.is_valid():
            form.save()
            return redirect("session_list")
    else:
        form = SleepSessionForm(instance=obj)
    return render(request, "session_form.html", {"form": form, "title": "Edit Sleep"})

@login_required
def goal_view(request):
    try:
        goal = request.user.sleep_goal
    except SleepGoal.DoesNotExist:
        goal = SleepGoal(user=request.user)
    if request.method == "POST":
        form = SleepGoalForm(request.POST, instance=goal)
        if form.is_valid():
            form.save()
            return redirect("dashboard")
    else:
        form = SleepGoalForm(instance=goal)
    return render(request, "goal.html", {"form": form})

@login_required
def import_csv(request):
    msg = None
    if request.method == "POST" and request.FILES.get("file"):
        f = request.FILES["file"].read().decode("utf-8")
        try:
            reader = csv.DictReader(io.StringIO(f))
            count = 0
            for row in reader:
                start = row.get("start")
                end = row.get("end")
                if not (start and end):
                    continue  # Skip rows missing start or end
                quality = int(row.get("quality", 3) or 3)
                latency = int(row.get("latency_minutes", 0) or 0)
                awakenings = int(row.get("awakenings", 0) or 0)
                tags = row.get("tags", "")
                notes = row.get("notes", "")
                SleepSession.objects.create(
                    user=request.user,
                    start=start,
                    end=end,
                    quality=quality,
                    latency_minutes=latency,
                    awakenings=awakenings,
                    tags=tags,
                    notes=notes,
                )
                count += 1
            msg = f"Imported {count} sessions."
        except Exception as e:
            msg = f"Error importing CSV: {str(e)}"
    return render(request, "import.html", {"message": msg})

@login_required
def export_csv(request):
    sessions = SleepSession.objects.filter(user=request.user).order_by("-start")
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="sleep_sessions.csv"'
    writer = csv.writer(response)
    writer.writerow(["start", "end", "quality", "latency_minutes", "awakenings", "tags", "notes", "duration_hours"])
    for s in sessions:
        writer.writerow([s.start.isoformat(), s.end.isoformat(), s.quality, s.latency_minutes, s.awakenings, s.tags, s.notes, s.duration_hours])
    return response


