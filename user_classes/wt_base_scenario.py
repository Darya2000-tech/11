
from locust import task, SequentialTaskSet, FastHttpUser, HttpUser, constant_pacing, constant_throughput, events
from config.config import cfg, logger
from utils.assertion import check_http_response
from utils.non_test_methods import open_csv_file, generateFlightsDates, generateFlightsDates
import sys, re, random  
from urllib.parse import quote_plus

class PurchaseFlightTicket (SequentialTaskSet):

    test_users_csv_filepath = './test_data/test_users.csv'
    test_flight_data_csv_filepath = './test_data/flight_details.csv'

    test_users_data = open_csv_file(test_users_csv_filepath)
    test_flight_data = open_csv_file(test_flight_data_csv_filepath)

    post_request_content_type_header ={
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    
    def on_start (self):


        @task 
        def uc_00_getHomePage(self) -> None:
            logger.info(f"Test data for users is:{self.test_users_data}")
            r00_0_headers = {'sec-fetch-mode' : 'navigate'}

            self.client.get(
                '/WebTours/',
                name ="req_00_0_getHomePage_/WebTours/",
                allow_redirects=False,
                #debug_stream=sys.stderr
            )	

            self.client.get(
                '/WebTours/header.html',
                name ="req_00_1_getHomePage_/WebTours/header.html",
                allow_redirects=False,
                #debug_stream=sys.stderr
            ) 
            r_02_url_param_signOff = 'true'

            self.client.get(
                f'/cgi-bin/welcome.pl?signOff={r_02_url_param_signOff}',
                name ="req_00_2_getHomePage_/cgi-bin/welcome.pl?signOff=true",
                allow_redirects=False,
                #debug_stream=sys.stderr
            )

            with self.client.get(
                f'/cgi-bin/nav.pl?in=home',
                name ="req_00_3_getHomePage_/cgi-bin/nav.pl?in=home",
                allow_redirects=False,
                catch_response = True
                #debug_stream=sys.stderr
            ) as req_00_3_response:
                check_http_response(req_00_3_response,'name="userSession"')
                print(f"\n____\n req_00_3_response.text: {req_00_3_response.text}\n____\n")

            self.user_session = re.search(r"name=\"userSession\" value=\"(.*)\"\/>" , req_00_3_response.text).group(1)

            logger.info(f"USER_SESSION PARAMETER: {self.user_session}")

            self.client.get(
                '/WebTours/home.html',
                name ="req_00_4_getHomePage_/WebTours/home.html",
                allow_redirects=False,
                #debug_stream=sys.stderr
            )

        @task
        def uc_01_LoginAction(self) -> None:
            r01_00_headers ={
                'Content-Type': 'application/x-www-form-urlencoded'
            }

            self.user_data_row = random.choice(self.test_users_data)
            logger.info(self.user_data_row)

            self.username =  self.user_data_row["username"]
            self.password = self.user_data_row["password"]

            logger.info (f"chosen username: {self.username} / password: {self.password}")

            r01_00_body =f"userSession={self.user_session}&username={self.username}&password={self.password}&login.x=0&login.y=0&JSFormSubmit=off"

            with self.client.post(
                '/cgi-bin/login.pl',
                name='req_01_0_LoginAction_/cgi-bin/login.pl',
                headers=r01_00_headers,
                data=r01_00_body,
                debug_stream = sys.stderr,
                cach_response=True
            ) as r_01_00_response:
                check_http_response (r_01_00_response, "User password was correct")
                logger.info(sys.stderr) 

            self.client.get(
                f'/cgi-bin/nav.pl?page=menu&in=home',
                name ="req_01_1_LoginAction_/cgi-bin/nav.pl?page=menu&in=home",
                allow_redirects=False,
                #debug_stream=sys.stderr
            )

            self.client.get(
                f'/cgi-bin/login.pl?intro=true',
                name ="req_01_2_LoginAction_/cgi-bin/login.pl?intro=true",
                allow_redirects=False,
                #debug_stream=sys.stderr
            )

        uc_00_getHomePage(self)
        uc_01_LoginAction(self)

    @task
    def uc_02_OpenFlightsTab(self):
        self.client.get(
            f'/cgi-bin/welcome.pl?page=search',
            name ="req_02_0_OpenFlightsTab_/cgi-bin/welcome.pl?page=search",
            allow_redirects=False,
            #debug_stream=sys.stderr
        )

        self.client.get(
            f'/cgi-bin/nav.pl?page=menu&in=flights',
            name ="req_02_1_OpenFlightsTab_/cgi-bin/nav.pl?page=menu&in=flights",
            allow_redirects=False,
            #debug_stream=sys.stderr
        )

        self.client.get(
            f'/cgi-bin/reservations.pl?page=welcome',
            name ="req_02_3_OpenFlightsTab_/cgi-bin/reservations.pl?page=welcome",
            allow_redirects=False,
            #debug_stream=sys.stderr
        )

    @task
    def uc_03_FindFlights_InputParams(self):
        self.flights_data_row = random.choice(self.test_flight_data)

        depart = self.user_data_row["depart"]
        arrive = self.user_data_row["arrive"]
        self.seat_pref = self.flights_data_row ["seat_pref"]
        self.seat_type = self.flights_data_row ["seat_type"]
        self.firstName = self.user_data_row ["firstName"]
        self.lastName = self.user_data_row ["lastName"]
        self.address1 = self.user_data_row ["address1"]
        self.address2 = self.user_data_row ["address2"]
        self.expDate = self.flights_data_row ["expDate"]

        dates_dict = generateFlightsDates()


        r03_00_body = f"advanceDiscount=0&depart={depart}&departDate={dates_dict["depart_date"]}&arrive={arrive}&returnDate={dates_dict["return_date"]}&numPassengers=1&seatPref={self.seat_pref}&seatType={self.seat_type}&findFlights.x=38&findFlights.y=11&.cgifields=roundtrip&.cgifields=seatType&.cgifields=seatPref"
        logger.info(f"uc03 request body: {r03_00_body}")

        with self.client.post(
            '/cgi-bin/reservations.pl',
            name='req_03_0_FindFlights_InputParams_/cgi-bin/reservations.pl',
            headers=self.post_request_content_type_header,
            data=r03_00_body,
            #debug_stream = sys.stderr,
            cach_response=True
        ) as r_03_00_response:
            check_http_response (r_03_00_response, "Flight departing from")
            logger.info(sys.stderr) 
            self.outboundFlight = re.search(r"\<input type=\"radio\" name=\"outboundFlight\" value=\"(.*)\">" , r_03_00_response.text).group(1)


    @task
    def uc_04_ChooseFlightOptions(self):
        self.flights_data_row = random.choice(self.test_flight_data)

        r04_00_body = f"outboundFlight={quote_plus(self.outboundFlight)}&numPassengers=1&advanceDiscount=0&seatType={self.seat_type}&seatPref={self.seat_pref}&reserveFlights.x=74&reserveFlights.y=7"
        logger.info(f"uc03 request body: {r04_00_body}")

        with self.client.post(
            '/cgi-bin/reservations.pl',
            name='req_04_0_ChooseFlightOptions/cgi-bin/reservations.pl',
            headers=self.post_request_content_type_header,
            data=r04_00_body,
            #debug_stream = sys.stderr,
            cach_response=True
        ) as r_04_00_response:
            check_http_response (r_04_00_response, "Total for 1 ticket(s) is = ")
            logger.info(sys.stderr)


    @task
    def uc_05_ConfirmFlightBooking(self):
        r05_00_body = f"firstName={self.firstName}&lastName={self.lastName}&address1={quote_plus(self.address1)}&address2={quote_plus(self.address2)}&pass1={quote_plus(self.firstName+ '' +self.lastName)}&creditCard={generateFlightsDates()}&expDate={self.expDate}&oldCCOption=&numPassengers=1&seatType={self.seat_type}&seatPref={self.seat_pref}&outboundFlight={quote_plus(self.outboundFlight)}&advanceDiscount=0&returnFlight=&JSFormSubmit=off&buyFlights.x=50&buyFlights.y=11&.cgifields=saveCC"
        logger.info(f"uc03 request body: {r05_00_body}")

        with self.client.post(
            '/cgi-bin/reservations.pl',
            name='req_05_0_ConfirmFlightBooking/cgi-bin/reservations.pl',
            headers=self.post_request_content_type_header,
            data=r05_00_body,
            debug_stream = sys.stderr,
            cach_response=True
        ) as r_05_00_response:
            check_http_response (r_05_00_response, "Total Charged to Credit Card #")
            logger.info(sys.stderr)     

class WebToursBaseUserClass (FastHttpUser): 
    wait_time = constant_pacing(cfg.pacing)
    host = cfg.url
    logger.info(f'WebToursBaseUserClass started. Host: {host}')
    tasks = [PurchaseFlightTicket]
