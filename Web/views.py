from django.shortcuts import render, redirect

items = [
    {
        'id': 1,
        'image': 'http://127.0.0.1:9000/images/1.jpg',
        'name': 'Восстановление удаленных данных',
        'price': 500,
        'description': 'Представляет собой восстановление случайно удаленных файлов или данных с отформатированных жестких дисков с помощью передовых технологий и опытных специалистов.'
    },
    {
        'id': 2,
        'image': 'http://127.0.0.1:9000/images/2.jpg',
        'name': 'Диагностика компьютера',
        'price': 300,
        'description': 'Определяет причину проблем с компьютером (медленная работа, зависания, ошибки) и находит эффективные решения.'
    },
    {
        'id': 3,
        'image': 'http://127.0.0.1:9000/images/3.jpg',
        'name': 'Установка и настройка программы',
        'price': 500,
        'description': 'Устанавливает и настраивает необходимое программное обеспечение для работы или личных нужд.'
    },
    {
        'id': 4,
        'image': 'http://127.0.0.1:9000/images/4.jpg',
        'name': 'Удаление вредоносного ПО',
        'price': 1500,
        'description': 'Избавляет от вирусов, шпионских программ и других вредоносных программ, защищая компьютер и личные данные.'
    },
    {
        'id': 5,
        'image': 'http://127.0.0.1:9000/images/5.jpg',
        'name': 'Настройка компьютерной периферии',
        'price': 1000,
        'description': 'Подключает и настраивает принтеры, сканеры и другие периферийные устройства для корректной работы.'
    },
    {
        'id': 6,
        'image': 'http://127.0.0.1:9000/images/6.jpg',
        'name': 'Оптимизация операционной системы',
        'price': 500,
        'description': 'Повышает производительность и стабильность компьютера путем оптимизации настроек операционной системы, удаления ненужных файлов и программ.'
    }
]

cartItemIds = [
    {
        'id': 1,
        'itemIds': [1, 5, 3]
    },
    {
        'id': 2,
        'itemIds': [2, 3, 1]
    },
    {
        'id': 3,
        'itemIds': [1, 6, 2]
    }
]

userCartId = 1

def getCartById(id):
    for cart in cartItemIds:
        if cart['id'] == id:
            return cart
    return None

def getItemById(id):
    for item in items:
        if item['id'] == id:
            return item
    return None

# Index controller
def indexController(request):
    cartAmount = 0
    cart = getCartById(userCartId)
    if cart != None:
        cartAmount = len(cart['itemIds'])

    search = ''
    if 'search' in request.GET:
        search = request.GET['search']
    
    data = {
        'items': [],
        'cartAmount': cartAmount,
        'search': search,
        'userCartId': userCartId
    }

    for item in items:
        if search.lower() in item['name'].lower():
            data['items'].append(item)

    return render(request, 'index.html', data)

# Item controller
def itemController(request, id):
    cartAmount = 0
    cart = getCartById(userCartId)
    if cart != None:
        cartAmount = len(cart['itemIds'])

    item = getItemById(id)
    if item == None:
        return redirect('index')

    return render(request, 'item.html', {
        'item': item,
        'cartAmount': cartAmount,
        'userCartId': userCartId
    })

# Shopping cart controller
def cartController(request, cartId):
    cart = getCartById(cartId)
    if cart == None:
        return redirect('index')

    data = {
        'items': [],
        'cartAmount': len(cart['itemIds']),
        'userCartId': cartId
    }
    for id in cart['itemIds']:
        item = getItemById(id)
        if item != None:
            data['items'].append({
                'name': item['name'],
                'price': item['price']
            })

    return render(request, 'cart.html', data)