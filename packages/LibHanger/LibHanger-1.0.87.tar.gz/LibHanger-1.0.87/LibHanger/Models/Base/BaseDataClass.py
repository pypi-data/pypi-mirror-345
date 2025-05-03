from dataclasses import dataclass
from abc import ABCMeta

@dataclass
class baseDataClass(metaclass=ABCMeta):
    """
    dataclass基底クラス
    
    Args:
        metaclass (_type_, optional): _description_. Defaults to ABCMeta.
    """

    def __new__(cls, *args, **kwargs):
        """
        __new__メソッドをオーバーライドして、dataclassを適用する
        """

        # dataclassを適用する
        dataclass(cls)
        # super().__new__を呼び出す
        return super().__new__(cls)