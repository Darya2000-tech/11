from config.config import logger
def check_http_response (response, param_to_chek) -> bool:
    try:
        assert param_to_chek in response.text
        
    except AssertionError as err:
        response.failure (f"Assertion error: text pattern {param_to_chek} was not found in response body!")
        result = False 
        logger.warning (f"Assertion error: text pattern {param_to_chek} was not found in response body!")

    else: 
          result = true    

    finally:
        return result      