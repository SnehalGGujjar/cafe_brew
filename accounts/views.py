from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.views import PasswordResetView, PasswordResetConfirmView, PasswordResetDoneView, PasswordResetCompleteView
from django.core.mail import send_mail
from django.shortcuts import render, redirect
from django.urls import reverse, reverse_lazy
from django.contrib import messages
from django.conf import settings
import random

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            # Staff (superuser or employee) require OTP
            if user.is_staff:
                code = f"{random.randint(100000, 999999)}"
                request.session['otp_user_id'] = user.id
                request.session['otp_code'] = code
                send_mail(
                    subject='Your OTP Code',
                    message=f'Your OTP code is {code}',
                    from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'no-reply@example.com'),
                    recipient_list=[user.email] if user.email else [],
                    fail_silently=True
                )
                return redirect('accounts:otp')
            else:
                login(request, user)
                return redirect('admin:index')
        else:
            messages.error(request, 'Invalid credentials')
    return render(request, 'accounts/login.html')

def otp_view(request):
    # Only for staff
    if request.method == 'POST':
        code = request.POST.get('code', '').strip()
        if code and code == request.session.get('otp_code'):
            from django.contrib.auth import get_user_model
            User = get_user_model()
            try:
                user = User.objects.get(id=request.session.get('otp_user_id'))
            except User.DoesNotExist:
                messages.error(request, 'Session expired. Please login again.')
                return redirect('accounts:login')
            login(request, user)
            # clear session otp
            for k in ('otp_code','otp_user_id'):
                if k in request.session: del request.session[k]
            return redirect('admin:index')
        messages.error(request, 'Invalid OTP.')
    return render(request, 'accounts/otp.html')

@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Password changed successfully.')
            return redirect('admin:index')
    else:
        form = PasswordChangeForm(user=request.user)
    return render(request, 'accounts/change_password.html', {'form': form})

class ForgotPasswordView(PasswordResetView):
    template_name = 'accounts/forgot.html'
    email_template_name = 'accounts/forgot_email.txt'
    success_url = reverse_lazy('accounts:forgot_done')

class ForgotPasswordDoneView(PasswordResetDoneView):
    template_name = 'accounts/forgot_done.html'

class ForgotPasswordConfirmView(PasswordResetConfirmView):
    template_name = 'accounts/forgot_confirm.html'
    success_url = reverse_lazy('accounts:forgot_complete')

class ForgotPasswordCompleteView(PasswordResetCompleteView):
    template_name = 'accounts/forgot_complete.html'
