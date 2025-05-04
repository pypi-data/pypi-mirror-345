from pydantic import BaseModel

class ExtRestResponse():

    def make_response(message:str):
        return {
            'Message':message
        }, 200

    def response_200(m_base:BaseModel):
        if m_base == None:
            return {'result': 'OK'}
        else:
            return m_base, 200
    
    def abort_400():
        return {
            'result':'error'
        }, 400
    
    def make_error_response(error:str):
        return error, 404
    
    def make_error(error:str, code:int):
        return error, code
    
    def make_response_200(text:str, key:str|None = None):
        if key == None:
            return {'Message':text}
        else:
            return {
                key: text
            }, 200