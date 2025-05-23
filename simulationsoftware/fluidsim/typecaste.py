# to convert string("[{key:val,key1:val1},{key:val,key2:val2}]") to list of dict([{key:val,key1:val1},{key:val,key2:val2}])
import ast
class TypeCasting():
    def __init__(self):
        pass

    def str_list_dict(self,data_str: str)->list:
        return list(eval(data_str))
    
    def str_dict(self,data_str:str)->dict:
        return ast.literal_eval(data_str)

        