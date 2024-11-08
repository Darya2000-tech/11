from locust import task, SequentialTaskSet, HttpUser, constant_pacing, constant_throughput, events
from config.config import cfg, logger

class PurchaseFlightTicket (SequentialTaskSet):
     @task 
     def uc_00_getHomePage(self) -> None:
       
        r00_01_headers = {
            'sec-fetch-mode' : 'navigate'
        }

        r00_01_responce = self.client.get(
            '/WebTours',
            name= "REQ_00_0_getHtml",
            allow_redirects=False,
            headers = r00_01_headers
        )
        print (r00_01_responce.status_code)
        print (r00_01_responce.text)
        print (r00_01_responce.request.headers)

class WebToursBaseUserClass (HttpUser): 
     wait_time = constant_pacing(cfg.pacing)

     host = cfg.url
     logger.info(f'WebToursBaseUserClass started. Host: {host}')
     tasks = [PurchaseFlightTicket]