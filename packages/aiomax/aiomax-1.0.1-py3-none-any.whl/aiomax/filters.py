from . import classes
import re


class equals:
    def __init__(self, content: str):
        '''
        :param content: Content to check
        
        Checks if the content equals to the given string
        '''
        self.content = content
    
    def __call__(self, obj: any):
        if hasattr(obj, "content"):
            return obj.content == self.content
        else:
            raise Exception(f"Class {type(object).__name__} has no content")


class has:
    def __init__(self, content: str):
        '''
        :param content: Content to check
        
        Checks if the content has the given string
        '''
        self.content = content
    
    def __call__(self, obj: any):
        if hasattr(obj, "content"):
            return self.content in obj.content
        else:
            raise Exception(f"Class {type(object).__name__} has no content")


class startswith:
    def __init__(self, prefix: str):
        '''
        :param prefix: Prefix to check
        
        Checks if the content starts with the given prefix
        '''
        self.prefix = prefix
    
    def __call__(self, obj: any):
        if hasattr(obj, "content"):
            return obj.content.startswith(self.prefix)
        else:
            raise Exception(f"Class {type(object).__name__} has no content")
        

class endswith:
    def __init__(self, suffix: str):
        '''
        :param suffix: Suffix to check
        
        Checks if the content ends with the given suffix
        '''
        self.suffix = suffix
    
    def __call__(self, obj: any):
        if hasattr(obj, "content"):
            return obj.content.endswith(self.suffix)
        else:
            raise Exception(f"Class {type(object).__name__} has no content")
        

class regex:
    def __init__(self, pattern: str):
        '''
        :param pattern: Regex pattern to check
        
        Checks if the content matches the given pattern
        '''
        self.pattern = pattern
    
    def __call__(self, obj: any):
        if hasattr(obj, "content"):
            return re.fullmatch(self.pattern, obj.body.text)
        else:
            raise Exception(f"Class {type(obj).__name__} has no content")


def papaya(obj: any):
    '''
    Checks if the content's second-to-last word of the content is "папайя".

    You do not need to call this.
    '''
    if hasattr(obj, "content"):
        words = obj.content.split()
        if len(words) < 2: return False
        return words[-2].lower() == "папайя"
    else:
        raise Exception(f"Class {type(object).__name__} has no content")