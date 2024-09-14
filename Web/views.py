from django.shortcuts import render, redirect

items = [
    {
        'id': 1,
        'image': 'http://127.0.0.1:9000/images/1.jpg',
        'name': 'Удаление или потеря данных',
        'description': 'Пользователь случайно удалил важные файлы или произошла ошибка в работе системы, приведшая к потере данных. Необходима услуга восстановления удалённых данных с помощью специальных программ и технологий.'
    },
    {
        'id': 2,
        'image': 'http://127.0.0.1:9000/images/2.jpg',
        'name': 'Неисправность компьютера',
        'description': 'Компьютер не включается, зависает или работает с перебоями. Требуется диагностика для выявления аппаратных или программных проблем, которые могут включать перегрев, сбой компонентов или конфликты программного обеспечения.'
    },
    {
        'id': 3,
        'image': 'http://127.0.0.1:9000/images/3.jpg',
        'name': 'Сбой в установке программы',
        'description': 'Во время установки программного обеспечения возникают ошибки, или программа после установки не работает корректно. Это может быть связано с несовместимостью ПО, нехваткой системных ресурсов или конфликтом с другими установленными приложениями.'
    },
    {
        'id': 4,
        'image': 'http://127.0.0.1:9000/images/4.jpg',
        'name': 'Обнаружение вредоносного ПО',
        'description': 'На устройстве обнаружены вирусы, трояны, рекламное ПО или другие вредоносные программы, которые могут угрожать безопасности данных или замедлять работу системы. Необходима услуга по их удалению и защите системы.'
    },
    {
        'id': 5,
        'image': 'http://127.0.0.1:9000/images/5.jpg',
        'name': 'Неисправность периферийного устройства',
        'description': 'Принтер, сканер, веб-камера или другое периферийное устройство не работает, не подключается к компьютеру или работает некорректно. Требуется настройка или устранение неполадок оборудования.'
    },
    {
        'id': 6,
        'image': 'http://127.0.0.1:9000/images/6.jpg',
        'name': 'Медленная работа системы',
        'description': 'Операционная система работает медленно, тормозит при выполнении задач, что может быть вызвано чрезмерным количеством запущенных процессов, накопившимися временными файлами или фрагментацией диска. Требуется оптимизация работы системы для улучшения её производительности.'
    }
]

appealItemIds = [
    {
        'id': 1,
        'items': [
            {
                'id': 1,
                'count': 1
            },
            {
                'id': 5,
                'count': 1
            },
            {
                'id': 3,
                'count': 2
            }
        ]
    },
    {
        'id': 2,
        'items': [
            {
                'id': 2,
                'count': 3
            },
            {
                'id': 3,
                'count': 1
            },
            {
                'id': 1,
                'count': 2
            }
        ]
    },
    {
        'id': 3,
        'items': [
            {
                'id': 1,
                'count': 5
            },
            {
                'id': 6,
                'count': 1
            },
            {
                'id': 2,
                'count': 3
            }
        ]
    }
]

userAppealId = 1

def getAppealById(id):
    for appeal in appealItemIds:
        if appeal['id'] == id:
            return appeal
    return None

def getItemById(id):
    for item in items:
        if item['id'] == id:
            return item
    return None

# Index controller
def indexController(request):
    appealAmount = 0
    appeal = getAppealById(userAppealId)
    if appeal != None:
        appealAmount = len(appeal['items'])

    search = ''
    if 'issue_name' in request.GET:
        search = request.GET['issue_name']
    
    data = {
        'items': [],
        'appealAmount': appealAmount,
        'search': search,
        'userAppealId': userAppealId
    }

    for item in items:
        if search.lower() in item['name'].lower():
            data['items'].append(item)

    return render(request, 'index.html', data)

# Item controller
def itemController(request, id):
    item = getItemById(id)
    if item == None:
        return redirect('index')

    return render(request, 'item.html', {
        'item': item
    })

# Appeal controller
def appealController(request, appealId):
    appeal = getAppealById(appealId)
    if appeal == None:
        return redirect('index')

    data = {
        'items': []
    }
    for itemData in appeal['items']:
        item = getItemById(itemData['id'])
        if item != None:
            data['items'].append({
                'name': item['name'],
                'image': item['image'],
                'count': itemData['count']
            })

    return render(request, 'appeal.html', data)