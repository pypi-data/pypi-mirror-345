from typing import Type,Iterable
from .models import SqlAlChemyBase
from .message import message
from .datebase import init_db
from .datebase import engine
from sqlalchemy import Engine,Insert
from pydantic import BaseModel

class BaseCurd(object):
    def __init__(self,db_engine:Engine = engine):
        '''
        初始化数据库引擎
        并且设置数据库引擎
        '''
        init_db()
        self.engine = db_engine
    
    def get_insert_ignore_stmt(self,table:Type[SqlAlChemyBase], chunk:int):
        """
        获取插入语句，支持 INSERT IGNORE
        
        :param table: SQLAlchemy 表模型类
        :param chunk: 批次数据，可以是字典或模型实例
        :param db_engine: 数据库引擎
        :return: INSERT IGNORE 语句
        """
        if self.engine.dialect.name == 'mysql':
            return Insert(table).values(chunk).prefix_with("IGNORE")
        elif self.engine.dialect.name == 'postgresql':
            return Insert(table).values(chunk).on_conflict_do_nothing()
        elif self.engine.dialect.name == 'sqlite':
            return Insert(table).values(chunk).prefix_with("OR IGNORE")
        else:  
            raise NotImplementedError(f"不支持的数据库类型: {self.engine.dialect.name}")
    def trans_objects_to_dict(self,objects:list[dict|Type[SqlAlChemyBase]|Type[BaseModel]]) -> list[dict]:
        """
        处理冲突对象
        
        :param model: SQLAlchemy 表模型类
        :param objects: 待处理的对象列表
        :return: 处理后的对象列表
        """
        if isinstance(objects[0],dict):
            return objects
        elif hasattr(objects[0],'__table__'):
            if hasattr(objects[0], 'to_dict'):
                return [obj.to_dict() for obj in objects]
            elif hasattr(objects[0], 'special_fields'):
                return  [{
                        c.name: getattr(obj, c.name)
                        for c in obj.__table__.columns if c.name not in obj.special_fields
                    } for obj in objects]
            else:
                return [
                    {
                        c.name: getattr(obj, c.name)
                        for c in obj.__table__.columns
                    } for obj in objects
                ]
        elif isinstance(objects[0],BaseModel):
            return [obj.model_dump() for obj in objects]
        else:
            raise TypeError("对象类型错误，请传入字典或模型实例")

    def bulk_insert_ignore_in_chunks(self,table:Type[SqlAlChemyBase], objects:Iterable, chunk_size=3000):
        """
        分块批量插入数据，支持 INSERT IGNORE
        
        :param table: SQLAlchemy 表模型类
        :param objects: 可迭代对象，每个元素代表一行数据(可以是字典或模型实例)
        :param chunk_size: 每批插入的数据量，默认为3000
        """
        try:
            # 检查objects是否为空
            objects = list(objects)  # 转换为列表以确保可多次迭代
            if not objects:
                message.warning('没有需要插入的数据')
                return 0
            
            # 确保chunk_size合理
            if chunk_size <= 0:
                raise ValueError("chunk_size必须大于0")
                
            total = len(objects)
            inserted_count = 0
            
            with self.engine.begin() as conn:
                for i in range(0, total, chunk_size):
                    # 获取当前批次的数据
                    chunk = objects[i:i + chunk_size]
                    
                    chunk = self.trans_objects_to_dict(chunk)
                    
                    # 构建并执行 INSERT IGNORE 语句
                    stmt = self.get_insert_ignore_stmt(table, chunk)
                    result = conn.execute(stmt)
                    inserted_count += result.rowcount
                    
                    message.info(f"已处理: {min(i + chunk_size, total)}/{total} 条记录")
            
            message.info(f"批量插入完成，共插入 {inserted_count} 条记录")
            return inserted_count
            
        except Exception as e:
            message.error(f"批量插入失败: {str(e)}")
            raise