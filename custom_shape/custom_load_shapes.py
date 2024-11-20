from locust import LoadTestShape 
from config.config import cfg, logger


class CustomLoadShape (LoadTestShape):
    match cfg.loadshape_type:
        case"baseline":
            stages = [
                {"duration": 60,"users": 1, "spawn_rate":1}
            ]

        case "flixedload":
           stages = [
                {"duration": 300,"users": 4, "spawn_rate":5}
            ]
        case "stages":
            stages =[
                {"duration": 30,"users": 10, "spawn_rate":2},
                {"duration": 60,"users": 20, "spawn_rate":2},
                {"duration": 90,"users": 30, "spawn_rate":2},
                {"duration": 120,"users": 40, "spawn_rate":2},
                {"duration": 150,"users": 50, "spawn_rate":2}
            ]

    def tick (self):
        run_time = self.get_run_time()
            
        for stage in self.stages:
            if run_time < stage["duration"]:
                tick_data = (stage["users"], stage["spawn_rate"]) 
                return tick_data 
        return None   