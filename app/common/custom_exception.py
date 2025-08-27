import sys

class CustomException(Exception):
    def __init__(self,message: str,error_detail: Exception = None):
        self.error_messge = self.get_detailed_error_message(message,error_detail)
        super().__init__(self.error_messge)

    @staticmethod
    def get_detailed_error_message(message: str, error_detail: Exception):
        _,_,exc_tb = sys.exc_info()
        file_name = exc_tb.tb_frame.f_code.co_filename if exc_tb else "Unknown file"
        line_number = exc_tb.tb_lineno if exc_tb else "Unknown line"
        return f"{message} | Error: {error_detail} | File: {file_name} | Line: {line_number}"
    
    def __str__(self):
        return self.error_messge
    
    