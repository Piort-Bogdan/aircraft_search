import json
import requests
import concurrent.futures
import threading

from django.shortcuts import render
from django.core.paginator import Paginator
from django.views.generic import TemplateView



class AircraftList(TemplateView):

    template_name = 'aircraft/search_aircraft.html'
    headers = {'Authorization': 'Token BN442rPF4zTfWAGQDqrZgjRWKznDfxUg9VK'}
    url = 'https://dir.aviapages.com/api/'

    def get(self, request, *args, **kwargs):

        def get_aircraft_list(page):

            data = []
            try:
                url = self.url + 'aircraft/'
                if len(request.GET.get('serial')) < 2 or len(request.GET.get('tail')) < 2:
                    query_serial,query_tail = ' ', ' '
                query_serial = request.GET.get('serial', '')
                query_tail = request.GET.get('tail', '')
                params = {'images': True, 'page': page, 'search_tail_number': query_tail,
                          'search_serial_number':query_serial, 'features': True}
                response = requests.get(url, headers=self.headers, params=params)
                aircraft_list = json.loads(response.text)['results']
                for item in aircraft_list:
                    data.append(item)
                print(f'Downloaded page aircraft {page}')
            except Exception as e:
                print(f'Error fetching page aircraft {page}: {e}')
            return data
        data = []
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = [executor.submit(get_aircraft_list, page) for page in range(1,2)]  # 593

            for f in concurrent.futures.as_completed(future):
                result = f.result()
                data += result
            print(len(data))

        def get_company_list(data):
            companies_list = []
            for company in data:
                try:
                    params_company = {'search_name': company['company_name']}
                    url_company = self.url + 'companies/'
                    response = requests.get(url_company, headers=self.headers, params=params_company)
                    companies = json.loads(response.text)['results']
                    for company_json in companies:
                        companies_list.append(company_json)
                except Exception as e:
                    print('не вышло', e)
            print(len(companies_list))
            return companies_list


        companies_list = []
        #
        #     # 181
        #
        #     for company in concurrent.futures.as_completed(companies):
        #         result = company.result()
        #         companies_list += result
        # print(len(companies_list))

        def get_airport_list(data):
            airport_list = []
            for icao in data:
                print('--', icao['home_base'])
                try:
                    url_airports = self.url + 'airports/'
                    params_airport = {'search_icao': icao['home_base']}
                    response = requests.get(url_airports, headers=self.headers, params=params_airport)
                    airports = json.loads(response.text)['results']
                    for airport in airports:
                        airport_list.append(airport)
                        # print(airport_list)
                except Exception as e:
                    print(f'не вышло')
            print(len(airport_list))
            return airport_list
        airport_list = []
        # with concurrent.futures.ThreadPoolExecutor() as executor:
        #     airports = executor.submit(get_airport_list, data) # 610
        #     for airport in concurrent.futures.as_completed(airports):
        #         result = airport.result()
        #         airport_list += result
        # print(len(airport_list))


        # with concurrent.futures.ThreadPoolExecutor() as executor:
        #     airports = executor.submit(get_airport_list, data)
        #     companies = executor.submit(get_company_list, data)
        #       # 610
        #     for company in concurrent.futures.as_completed(companies):
        #         try:
        #             result = company.result()
        #             companies_list += result
        #         except Exception as e:
        #             print(f'eroe {e}')
        #     for airport in concurrent.futures.as_completed(airports):
        #         try:
        #             result = airport.result()
        #             airport_list += result
        #         except Exception as ee:
        #             print(f'eee {ee}')
        # paginator
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
            'companies': get_company_list(page_obj),
            'airports': get_airport_list(page_obj)
        }
        return render(request, self.template_name, context)

    # def get_context_data(self, **kwargs):
    #     context = super().get_context_data(**kwargs)
    #     context['data'] = self.get_list(request)
    #     return context
    #
    #     # paginator
    #     paginator = Paginator(data, 300)
    #     page_number = request.GET.get('page')
    #     page_obj = paginator.get_page(page_number)
    #
    #     try:
    #         current_page = int(page_number)
    #     except:
    #         current_page = 1

