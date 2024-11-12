
from locust import task, SequentialTaskSet, FastHttpUser, HttpUser, constant_pacing, constant_throughput, events
from config.config import cfg, logger
from utils.assertion import check_http_response
from utils.non_test_methods import open_csv_file
import sys, re, random  

class PurchaseFlightTicket (SequentialTaskSet):

    test_users_csv_filepath = './test_data/test_users.csv'
    
    def on_start (self):


        @task 
        def uc_00_getHomePage(self) -> None:
            self.test_users_data = open_csv_file(self.test_users_csv_filepath)
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

            r01_00_body =f"userSession={self.user_session}&username={username}&password={password}&login.x=0&login.y=0&JSFormSubmit=off"

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
                '/cgi-bin/nav.pl?page=menu&in=home',
                name ="req_01_1_LoginAction_/cgi-bin/nav.pl?page=menu&in=home",
                allow_redirects=False,
                #debug_stream=sys.stderr
            )

            self.client.get(
                '/cgi-bin/login.pl?intro=true',
                name ="req_01_2_LoginAction_/cgi-bin/login.pl?intro=true",
                allow_redirects=False,
                #debug_stream=sys.stderr
            )

        uc_00_getHomePage(self)
        uc_01_LoginAction(self)

    @task
    def mydummy_task (self):
        print ('ЧТО-НИБУДЬ')

class WebToursBaseUserClass (FastHttpUser): 
    wait_time = constant_pacing(cfg.pacing)
    host = cfg.url
    logger.info(f'WebToursBaseUserClass started. Host: {host}')
    tasks = [PurchaseFlightTicket]
