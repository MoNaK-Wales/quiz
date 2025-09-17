from django.shortcuts import render

# Create your views here.
def main_page(request):
    return render(request, 'browser/main.html')

def profile(request):
    user = request.user
    context = {'user': user}
    return render(request, 'browser/profile.html', context)