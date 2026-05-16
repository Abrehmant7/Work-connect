from django.contrib.auth import authenticate, login, logout
from django.shortcuts import redirect, render

from recruiter.forms import CustomUserCreationForm


def signUp(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST, request.FILES)

        if form.is_valid():
            user = form.save()
            login(request, user)

            if user.user_type == 'representative':
                return redirect("representative_profile")
            elif user.user_type == 'applicant':
                return redirect("applicant_profile")

    else:
        form = CustomUserCreationForm()

    return render(request, "auth/sign_up.html", {'form': form})


def logIn(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)

            if user.user_type == 'applicant':
                if not hasattr(user, 'applicant_profile'):
                    return redirect("applicant_profile")

            elif user.user_type == "representative":
                if not hasattr(user, 'representative_profile'):
                    return redirect("representative_profile")

            return redirect("/")

        return render(request, 'auth/log_in.html', {"error": "invalid credentials"})

    return render(request, "auth/log_in.html")


def logOut(request):
    logout(request)
    return redirect('login')
