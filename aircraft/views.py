import json
import requests

from django.shortcuts import render
from django.core.paginator import Paginator


def search_aircraft(request):
    query = request.GET.get('q', 'По-умолчанию')
    print('Строка---------------', query)

    url = 'https://dir.aviapages.com/api/aircraft/'
    headers = {'Authorization': 'Token BN442rPF4zTfWAGQDqrZgjRWKznDfxUg9VK'}
    params = {'images': True, 'page':30}
    response = requests.get(url, headers=headers, params=params)
    print(response.url)
    print(type(response.text), response.status_code)
    data = json.loads(response.text)['results']
    dd = json.loads(response.text)['per_page']=299
    print(len(data))

    # paginator
    paginator = Paginator(data, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)







    # print(data)
    return render(request, 'aircraft/search_aircraft.html', {'data': data, 'page_obj':page_obj})
