import LibHanger.Library.uwLogger as Logger
from LibHanger.Library.uwConfig import cmnConfig
from LibHanger.Library.uwDeclare import uwDeclare as de


class globalValues:
    """
    オブジェクト共有クラス
    """

    def __init__(self):
        """
        コンストラクタ
        """

        self.config: cmnConfig = None
        """ 共通設定 """

        self.platForm = de.platFormStruct()
        """ プラットフォーム構造体 """


# インスタンス生成(import時に実行される)
gv = globalValues()


class configer:
    """
    共通設定クラス
    """

    def __init__(self, tgv, filePath, configFolderName):
        """
        コンストラクタ
        """

        # 共通設定(ノーマル)
        ccfg = cmnConfig()
        ccfg.getConfig(filePath, configFolderName)

        # ロガー設定
        Logger.setting(ccfg)

        # 共通設定
        tgv.config = ccfg
