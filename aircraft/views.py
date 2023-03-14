from django.shortcuts import render
import json
import requests


def search_aircraft(request):
    query = request.GET.get('q', 'По-умолчанию')
    print('Строка---------------', query)

    url = 'https://dir.aviapages.com/api/aircraft/'
    headers = {'Authorization': 'Token BN442rPF4zTfWAGQDqrZgjRWKznDfxUg9VK'}
    response = requests.get(url, headers=headers)
    print(type(response.text), response.status_code)
    data = json.loads(response.text)
    print(data['count'])
    return render(request, 'aircraft/search_aircraft.html', {'data': data})
