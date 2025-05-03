from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.orm import DeclarativeBase
from dotenv import load_dotenv
from contextlib import contextmanager
from typing import Generator, Type
from .models import SqlAlChemyBase
import os
from .message import message

# 加载环境变量
load_dotenv()

# 获取数据库连接信息
DB_HOST: str|None = os.getenv("DB_HOST",None)
DB_PORT: str = os.getenv("DB_PORT", "3306")
DB_USER: str = os.getenv("DB_USERNAME", "root")
DB_PASSWORD: str = os.getenv("DB_PASSWORD", "password")
DB_NAME: str = os.getenv("DB_NAME_DEFINE", "test_db")

# 创建数据库连接URL
DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}" if DB_HOST else None

# 创建数据库引擎
engine = create_engine(DATABASE_URL) if DATABASE_URL else None

# 创建会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine) if engine else None

def init_db(sqlalchemy_base: Type[DeclarativeBase] | None = None) -> None:
    """
    初始化数据库表结构
    
    Args:
        sqlalchemy_base: 继承自DeclarativeBase的基类，如果为None则使用默认SqlAlChemyBase
    
    Raises:
        ValueError: 当数据库配置缺失时
        Exception: 当表创建失败时
    """
    if not DB_HOST:
        error_msg = "数据库连接信息未配置，请检查.env文件中的DB_HOST设置"
        message.error(error_msg)
        raise ValueError(error_msg)
    
    if not engine:
        error_msg = "数据库引擎初始化失败"
        message.error(error_msg)
        raise RuntimeError(error_msg)
    
    try:
        base = sqlalchemy_base or SqlAlChemyBase
        base.metadata.create_all(bind=engine)
        message.info("数据库表初始化成功")
    except Exception as e:
        error_msg = f"数据库表初始化失败: {str(e)}"
        message.error(error_msg)
        raise RuntimeError(error_msg) from e

@contextmanager
def get_session(auto_commit: bool = True) -> Generator[Session, None, None]:
    """
    获取数据库会话上下文
    
    Args:
        auto_commit: 是否在上下文结束时自动提交事务
        
    Yields:
        Session: SQLAlchemy会话对象
        
    Raises:
        RuntimeError: 如果会话工厂未正确初始化
    """
    if not SessionLocal:
        error_msg = "会话工厂未初始化，请先检查数据库配置"
        message.error(error_msg)
        raise RuntimeError(error_msg)
    
    session = SessionLocal()
    try:
        yield session
        if auto_commit:
            session.commit()
    except Exception as e:
        session.rollback()
        message.error(f"数据库操作出错: {str(e)}，已回滚事务")
        raise  # 重新抛出异常以便调用方处理
    finally:
        session.close()
