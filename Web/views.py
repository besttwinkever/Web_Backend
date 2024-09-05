from django.http import HttpResponse
from django.shortcuts import render

items = [
    {
        'id': 1,
        'image': 'http://127.0.0.1:9000/images/1.jpg',
        'name': 'Восстановление удаленных данных',
        'price': 500,
        'description': ''
    },
    {
        'id': 2,
        'image': 'http://127.0.0.1:9000/images/2.jpg',
        'name': 'Диагностика компьютера',
        'price': 300,
        'description': ''
    },
    {
        'id': 3,
        'image': 'http://127.0.0.1:9000/images/3.jpg',
        'name': 'Установка и настройка программы',
        'price': 500,
        'description': ''
    },
    {
        'id': 4,
        'image': 'http://127.0.0.1:9000/images/4.jpg',
        'name': 'Удаление вредоносного ПО',
        'price': 1500,
        'description': ''
    },
    {
        'id': 5,
        'image': 'http://127.0.0.1:9000/images/5.jpg',
        'name': 'Настройка компьютерной периферии',
        'price': 1000,
        'description': ''
    },
    {
        'id': 6,
        'image': 'http://127.0.0.1:9000/images/6.jpg',
        'name': 'Оптимизация операционной системы',
        'price': 500,
        'description': ''
    }
]

cartItemIds = [1, 2]

def index(request):
    search = ''
    if 'search' in request.POST:
        search = request.POST['search']
    
    data = {
        'items': [],
        'cartAmount': len(cartItemIds),
        'search': search
    }

    for item in items:
        if search.lower() in item['name'].lower():
            data['items'].append(item)

    return render(request, 'index.html', data)

def item(request):
    return HttpResponse('Item details')

def cart(request):
    return HttpResponse('Shopping cart')