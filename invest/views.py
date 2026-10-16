import random
from django.shortcuts import render
from django.http import JsonResponse

def webapp_home(request):
    """WebApp sahifasini ko'rsatish"""
    return render(request, 'index.html')

def get_captcha(request):
    """Tasodifiy matematik misol generatsiya qilish"""
    num1 = random.randint(10, 50)
    num2 = random.randint(1, 20)
    op = random.choice(['+', '-'])
    
    if op == '+':
        ans = num1 + num2
    else:
        ans = num1 - num2
        
    request.session['captcha_ans'] = ans
    return JsonResponse({
        'question': f"{num1} {op} {num2} = ?"
    })

def verify_captcha(request):
    """Captcha javobini tekshirish va tanga berish"""
    user_ans = request.GET.get('answer', '')
    saved_ans = request.session.get('captcha_ans')
    
    try:
        if saved_ans is not None and int(user_ans) == saved_ans:
            # Captcha to'g'ri yechilsa 100 tanga mukofot
            return JsonResponse({'status': 'ok', 'reward': 100, 'message': 'To‘g‘ri! +100 tanga qo‘shildi 🎉'})
        else:
            return JsonResponse({'status': 'error', 'message': 'Noto‘g‘ri javob! Qayta urinib ko‘ring.'})
    except ValueError:
        return JsonResponse({'status': 'error', 'message': 'Faqat son kiriting!'})
