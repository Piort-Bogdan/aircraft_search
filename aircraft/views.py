import json
import requests
import concurrent.futures

from django.shortcuts import render
from django.core.paginator import Paginator
from django.views.generic import TemplateView

from aircraft_search.settings import API_TOKEN


class AircraftList(TemplateView):
    ''' Aicraft API list View '''

    template_name = 'aircraft/search_aircraft.html'
    # HEADERS = {'Authorization': API_TOKEN}
    HEADERS = {'Authorization': 'Token BN442rPF4zTfWAGQDqrZgjRWKznDfxUg9VK'}
    URL = 'https://dir.aviapages.com/api/'

    def get(self, request, *args, **kwargs):

        data_list = []
        companies_list = []
        airport_list = []
        count = self.get_page_count(request)

        # make item list form search
        with concurrent.futures.ThreadPoolExecutor() as executor:
            aircraft_future = [executor.submit(self.get_aircraft_list, request, page) for page in range(1, round(count))]

            ok = concurrent.futures.wait(aircraft_future)
            try:
                for future in ok.done:
                    result = future.result()
                    data_list += result
                print(len(data_list))
            except Exception as e:
                print(f'Error - {e}')

        # make list of companies from search list
        with concurrent.futures.ThreadPoolExecutor() as executor:
            companies_future = [executor.submit(self.get_company_detail, data) for data in data_list]

            try:
                for future_comp in concurrent.futures.as_completed(companies_future):
                    result_comp = future_comp.result()
                    companies_list += result_comp
                print(f'{len(companies_list)}, List Company')
            except Exception as exp:
                print(f'Getting error = {exp}')

        # make list of airports from search list
        with concurrent.futures.ThreadPoolExecutor() as executor:
            airports_future = [executor.submit(self.get_airport_detail, data) for data in data_list]
            try:
                for future_airport in concurrent.futures.as_completed(airports_future):
                    result_airport = future_airport.result()
                    airport_list += result_airport
                print(f'airport list {len(airport_list)}')
            except Exception as exp:
                print(f'Getting error = {exp}')

        # pagination
        paginator = Paginator(data_list, 300)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        try:
            current_page = int(page_number)
        except:
            current_page = 1

        context = {
            'page_obj': page_obj,
            'current_page': current_page,
            'companies': companies_list,
            'airports': airport_list,
        }
        return render(request, self.template_name, context)

    def get_aircraft_list(self, request, page):

        ''' Get aircraft list '''

        if request.GET.get('serial') == '' and request.GET.get('tail') == '':
            params = {'images': True, 'features': True }
        else:
            url = self.URL + 'aircraft/'
            query_serial = request.GET.get('serial')
            query_tail = request.GET.get('tail')
            params = {'features': True, 'images': True, 'ordering': 'serial_number', 'search_tail_number': query_tail,
                      'search_serial_number': query_serial}
            try:
                response = requests.get(url, headers=self.HEADERS, params=params)
                aircraft = json.loads(response.text)['results']
            except Exception as e:
                print(f'error - {e}')
            return aircraft

    def get_company_detail(self, data):
        
        ''' GET company detail information '''
        companies = []
        try:
            params_company = {'search_name': data['company_name']}
            url_company = self.URL + 'companies/'
            response = requests.get(url_company, headers=self.HEADERS, params=params_company)
            companies = json.loads(response.text)['results']
        except Exception as e:
            print(f'Get_company_detail Error - {e}')
        return companies

    def get_airport_detail(self, data):

        ''' GET airport detail information '''
        airports = []
        try:
            url_airports = self.URL + 'airports/'
            params_airport = {'search_icao': data['home_base']}
            response = requests.get(url_airports, headers=self.HEADERS, params=params_airport)
            airports = json.loads(response.text)['results']
        except Exception as e:
            print(f'Airport detail gettin error - {e}')
        return airports

    def get_page_count(self, request):

        url = self.URL + 'aircraft/'
        query_serial = request.GET.get('serial')
        query_tail = request.GET.get('tail')
        params = {'features': True, 'images': True, 'ordering': 'serial_number', 'search_tail_number': query_tail,
                  'search_serial_number': query_serial}
        response = requests.get(url, headers=self.HEADERS, params=params)
        count = json.loads(response.text)['count']/20
        return count