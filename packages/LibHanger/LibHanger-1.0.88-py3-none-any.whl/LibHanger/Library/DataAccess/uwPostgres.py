from LibHanger.Library.DataAccess.Base.uwDataAccess import uwDataAccess
from LibHanger.Library.uwConfig import cmnConfig


class uwPostgreSQL(uwDataAccess):
    """
    uwPostgreSQLクラス
    """

    def __init__(
        self, config: cmnConfig, __instance_on_dbopen=False
    ) -> None:
        """
        コンストラクタ

        Parameters
        ----------
        config : cmnConfig
            共通設定クラス
        __instance_on_dbopen : bool
            Open Database at the same time as instance creation
        """
        super().__init__(config, __instance_on_dbopen)
