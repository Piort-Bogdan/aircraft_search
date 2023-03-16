import json
import requests

from django.shortcuts import render
from django.core.paginator import Paginator



def search_aircraft(request):
    if len(str(request.GET.get)) >= 2:
        query = request.GET.get('search', '')
    else:
        query = ' '
    print('Строка---------------', query)
    print(request)
    url = 'https://dir.aviapages.com/api/aircraft/'
    headers = {'Authorization': 'Token BN442rPF4zTfWAGQDqrZgjRWKznDfxUg9VK'}

    params = {'images': True, 'page':1, 'search': query}
    response = requests.get(url, headers=headers, params=params)
    data = []

    # ------------
    # k = 1
    # while response.status_code == 200:
    #     params = {'images': True, 'page': k, 'search': query}
    #     response = requests.get(url, headers=headers, params=params)
    #     k += 1
    # ------------

    i = 1
    for i in range(1, 2):
        try:
            params = {'images': True, 'page': i, 'search': query}
            print(response.url)
            response = requests.get(url, headers=headers, params=params)
            de = json.loads(response.text)['results']
            for i in de:
                print(i)
                data.append(i)
            # print(len(data), data)
            i += 1
            print(i)
        except:
            continue

    # print('Итоговый словарь -', data, len(data))

    # paginator
    paginator = Paginator(data, 300)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    try:
        current_page = int(page_number)
    except:
        current_page = 1



    return render(request, 'aircraft/search_aircraft.html', {'data': data,
                                                             'page_obj': page_obj,
                                                             'current_page': current_page})
