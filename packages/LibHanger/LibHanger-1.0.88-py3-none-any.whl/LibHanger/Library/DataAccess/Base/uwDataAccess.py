from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.session import Session as BaseSession
from sqlalchemy.engine import Engine as BaseEngine
from sqlalchemy.exc import SQLAlchemyError
import LibHanger.Library.uwLogger as Logger
from LibHanger.Library.uwLogger import loggerDecorator
from LibHanger.Library.uwConfig import cmnConfig


class uwDataAccess:
    """
    データアクセスクラス
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

        self.__config = config
        """ 共通設定 """

        self.__session: BaseSession = None
        """ DBセッション """

        self.__engine: BaseEngine = None
        """  sqlalchemy - engine """

        self.__instance_on_dbopen = __instance_on_dbopen
        """  instance_on_dbopen Flag """

    def __enter__(self):
        """
        ContextManger - enter
        """

        # Session - Open
        if self.__instance_on_dbopen:
            self.openSession(True)

        return self
    
    def __exit__(self, ex_type, ex_value, trace):
        """
        ContextManger - exit

        Parameters
        ----------
            ex_type : Any
                ex_type
            ex_value : Any
                ex_value
            trace : Any
                trace
        """

        # with内で例外発生時
        if ex_type != None:
            # ログ出力
            Logger.logging.error(f"Exception Type={ex_type}")
            Logger.logging.error(f"Exception Value={ex_value}")
            Logger.logging.error(f"Stack trace={trace}")

        # Session - Close
        self.closeSession()

        # Trueを返して例外を握りつぶす
        return True

    @property
    def session(self):
        """
        DBセッション
        """

        return self.__session

    @property
    def autoCommit(self):
        """
        autocommit
        """

        return self.__session.autocommit

    def getConnectionString(self):
        """
        接続文字列取得
        """

        # 接続文字列生成
        return "{}://{}:{}@{}:{}/{}".format(
            self.__config.ConnectionString.DatabaseKind,
            self.__config.ConnectionString.User,
            self.__config.ConnectionString.Password,
            self.__config.ConnectionString.Host,
            self.__config.ConnectionString.Port,
            self.__config.ConnectionString.DatabaseName,
        )

    @loggerDecorator("Open Session")
    def openSession(self, __autocommit=False, __expire_on_commit=False):
        """
        sessionを開く

        Parameters
        ----------

        __autocommit : bool
            autocommit
        __expire_on_commit : bool
            expire_on_commit
            Falseの場合、セッションをCommit,Close後のインスタンスアクセスを許可する
        """

        # engine生成
        self.__engine = self.createEngine()

        # session生成
        self.__session = self.createSession(self.__engine, __autocommit)

        # expire_on_commit
        self.__session.expire_on_commit = __expire_on_commit

    @loggerDecorator("Begin Transaction")
    def beginTransaction(self):
        """
        トランザクションを開始する
        """
        # トランザクション開始
        self.__session.begin()

    @loggerDecorator("Commit Seesion")
    def commit(self):
        """
        commit

        Parameters
        ----------

        None
        """

        # Session - Commit
        self.__session.commit()

        # autocommit - On
        self.__session.autocommit = True

    @loggerDecorator("Commit Rollback")
    def rollback(self):
        """
        rollback

        Parameters
        ----------

        None
        """

        # Session - Rollback
        self.__session.rollback()

        # autocommit - On
        self.__session.autocommit = True

    @loggerDecorator("Close Seesion")
    def closeSession(self):
        """
        session閉じる

        Parameters
        ----------

        None
        """

        # Seesion - Close
        if self.__session != None:
            self.__session.close()
            self.__session = None

    @loggerDecorator("Create Engine")
    def createEngine(self):
        """
        engine生成

        Parameters
        ----------

        None
        """

        # 接続文字列取得
        connectionString = self.getConnectionString()

        # engine生成
        eng = create_engine(connectionString, echo=False)

        # 生成したengineを返す
        return eng

    @loggerDecorator("Connection - DataBase")
    def dbConnect(self, eng: BaseEngine):
        """
        database接続

        Parameters
        ----------
        eng : _engine.Engine
            Engine
        """

        # 生成したengineから接続を返す
        return eng.connect()

    @loggerDecorator("Create - Session")
    def createSession(self, eng, __autocommit) -> BaseSession:
        """
        sqlalchemy用セッション生成

        Parameters
        ----------
        eng : _engine.Engine
            Engine
        __autocommit : bool
            autocommit
        """

        # sessionmakerで返す
        Session = sessionmaker(bind=eng, autocommit=__autocommit)

        # 戻り値として返す
        return Session()

    def sqlExecute(self, sql):
        """
        sql実行

        Parameters
        ----------
        sql : str
            実行対象SQL
        """

        updateCount = 0

        # SQL実行
        try:
            # CursorResult取得
            cursorResult = self.__session.execute(sql)
            # 更新件数
            updateCount = cursorResult.rowcount
        except SQLAlchemyError as e:
            # 戻り値に-1セット
            updateCount = -1
            # ログ出力
            Logger.logging.error(e)
            # SQLAlchemyErrorをThrow
            raise SQLAlchemyError

        return updateCount
