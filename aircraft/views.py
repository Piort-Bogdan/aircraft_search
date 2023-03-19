import json
import os

import requests
import concurrent.futures

from django.shortcuts import render
from django.core.paginator import Paginator
from django.views.generic import TemplateView

from aircraft_search.settings import API_TOKEN


class AircraftList(TemplateView):
    ''' Aicraft API list View '''


    template_name = 'aircraft/search_aircraft.html'
    HEADERS = {'Authorization': API_TOKEN}
    URL = 'https://dir.aviapages.com/api/'

    def get(self, request, *args, **kwargs):

        def get_aircraft_list(page):

            ''' Get aircraft list '''

            data = []
            try:
                url = self.URL + 'aircraft/'
                if len(request.GET.get('serial')) < 2 or len(request.GET.get('tail')) < 2:
                    query_serial, query_tail = ' ', ' '
                query_serial = request.GET.get('serial', '')
                query_tail = request.GET.get('tail', '')
                params = {'images': True, 'page': page, 'search_tail_number': query_tail,
                          'search_serial_number': query_serial, 'features': True}
                response = requests.get(url, headers=self.HEADERS, params=params)
                aircraft_list = json.loads(response.text)['results']
                for item in aircraft_list:
                    data.append(item)
                print(f'Downloaded page aircraft {page}')
            except Exception as e:
                print(f'Error fetching page aircraft {page}: {e}')
            return data

        data = []
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = [executor.submit(get_aircraft_list, page) for page in range(1, 593)]  # 593

            for f in concurrent.futures.as_completed(future):
                result = f.result()
                data += result

        def get_company_detail(data):

            ''' GET company detail information '''

            companies_list = []
            for company in data:
                try:
                    params_company = {'search_name': company['company_name']}
                    url_company = self.URL + 'companies/'
                    response = requests.get(url_company, headers=self.HEADERS, params=params_company)
                    companies = json.loads(response.text)['results']
                    for company_json in companies:
                        companies_list.append(company_json)
                except Exception as e:
                    print(f'Company detail getting error - {e}')
            return companies_list

        def get_airport_detail(data):

            ''' GET airport detail information '''

            airport_list = []
            for icao in data:
                try:
                    url_airports = self.URL + 'airports/'
                    params_airport = {'search_icao': icao['home_base']}
                    response = requests.get(url_airports, headers=self.HEADERS, params=params_airport)
                    airports = json.loads(response.text)['results']
                    for airport in airports:
                        airport_list.append(airport)
                except Exception as e:
                    print(f'Airport detail gettin error - {e}')
            return airport_list

        airport_list = []

        #pagination
        paginator = Paginator(data, 300)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        try:
            current_page = int(page_number)
        except:
            current_page = 1

        context = {
            'data': data,
            'page_obj': page_obj,
            'current_page': current_page,
            'companies': get_company_detail(data),
            'airports': get_airport_detail(data)
        }
        return render(request, self.template_name, context)
