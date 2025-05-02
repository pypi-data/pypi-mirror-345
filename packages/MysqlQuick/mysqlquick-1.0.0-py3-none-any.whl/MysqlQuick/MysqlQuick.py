import os
import time
import MySQLdb
import logging
import functools
from MySQLdb import Error
from dbutils.pooled_db import PooledDB
from typing import Union, List, Dict, Tuple, Any


# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [%(levelname)s] %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger('MysqlQuick:')


class MysqlQuick:
    # 初始化数据库连接池
    def __init__(self, dbName="mydb", host='localhost', user='root', password='root', charset='utf8mb4', poolSize=None):
        self.poolSize = poolSize or os.cpu_count() * 5
        self._initDatabase(dbName, host, user, password, charset)
        self.pool = self._createPool(dbName, host, user, password, charset, self.poolSize)
        logger.info(f'💾 ✅ 数据库就绪 | 连接池大小: {self.poolSize}')


    # 初始化数据库（如果不存在则创建）
    def _initDatabase(self, dbName: str, host: str, user: str, password: str, charset: str) -> None:
        try:
            conn = MySQLdb.connect(host=host, user=user, password=password, charset=charset)
            with conn.cursor() as cursor: cursor.execute(f"CREATE DATABASE IF NOT EXISTS {dbName}")
            conn.commit()
        except Error as e:
            logger.error(f'📥 ❌ 数据库初始化失败 | 错误: {str(e)}')
            return


    # 创建数据库连接池
    def _createPool(self, dbName: str, host: str, user: str, password: str, charset: str, poolSize: int) -> PooledDB:
        return PooledDB(
            creator=MySQLdb,
            mincached=2,
            maxconnections=poolSize,
            host=host,
            user=user,
            passwd=password,
            db=dbName,
            charset=charset,
            cursorclass=MySQLdb.cursors.DictCursor,
            autocommit=True  # 自动提交事务
        )


    # 执行 SQL 语句的内部方法
    def _execute(self, sql: str, args: Tuple = None, isSelect: bool = False) -> Union[int, List[Dict]]:
        startTime = time.time()
        try:
            with self.pool.connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(sql, args or ())
                    if isSelect:
                        result = cursor.fetchall()
                        logger.info(f'🔍 ✅ 查询完成 | 结果数: {len(result)} | 耗时: {time.time()-startTime:.4f}s')
                        return result
                    else:
                        rowCount = cursor.rowcount
                        logger.info(f'⚡ ✅ 执行成功 | 影响行数: {rowCount} | 耗时: {time.time()-startTime:.4f}s')
                        return rowCount
        except Error as e:
            logger.info(f'⚡ ❌ SQL执行失败 | 错误: {str(e)} | SQL: {sql} | 参数: {args}')
            return


    # 创建数据表（带索引优化）
    def create(self, tableName: str, columns: Dict[str, str]) -> bool:
        try:
            cols = ', '.join([f"{k} {v}" for k, v in columns.items()])
            sql = f"CREATE TABLE IF NOT EXISTS {tableName} ({cols})"
            self._execute(sql)
            logger.info(f'📝 ✅ 表创建成功: {tableName}')
            return True
        except Error: return False


    # 插入单条数据
    def insert(self, tableName: str, data: Dict) -> int:
        keys = list(data.keys())
        values = tuple(data.values())
        placeholders = ','.join(['%s'] * len(keys))
        sql = f"INSERT INTO {tableName} ({','.join(keys)}) VALUES ({placeholders})"
        return self._execute(sql, values)


    # 查询数据（带缓存优化）
    def select(self, tableName: str, where: Dict = None, fields: List[str] = None) -> List[Dict]:
        # 转换参数为可哈希类型以支持缓存
        whereHashable = self._convertToHashable(where)
        fieldsHashable = tuple(fields) if fields else None
        return self._selectCached(tableName, whereHashable, fieldsHashable)


    # 带缓存的查询方法
    @functools.lru_cache(maxsize=1024)
    def _selectCached(self, tableName: str, whereHashable: tuple, fieldsHashable: tuple) -> List[Dict]:
        where = dict(whereHashable) if whereHashable else None
        fields = list(fieldsHashable) if fieldsHashable else None
        
        selectFields = '*' if not fields else ','.join(fields)
        whereClause, params = self._buildWhereClause(where) if where else ('1=1', [])
        sql = f"SELECT {selectFields} FROM {tableName} WHERE {whereClause}"
        
        return self._execute(sql, params, isSelect=True)


    # 更新数据
    def update(self, tableName: str, setData: Dict, where: Dict) -> int:
        setClause, setParams = self._buildSetClause(setData)
        whereClause, whereParams = self._buildWhereClause(where)
        sql = f"UPDATE {tableName} SET {setClause} WHERE {whereClause}"
        return self._execute(sql, setParams + whereParams)


    # 删除数据
    def delete(self, tableName: str, where: Dict = None) -> int:
        whereClause, params = self._buildWhereClause(where) if where else ('1=1', [])
        sql = f"DELETE FROM {tableName} WHERE {whereClause}"
        return self._execute(sql, params)


    # 执行原生 SQL 语句
    def sql(self, sql: str, args: Tuple = None) -> Union[int, List[Dict]]:
        isSelect = sql.strip().upper().startswith("SELECT")
        return self._execute(sql, args, isSelect)


    # 构建 WHERE 子句
    def _buildWhereClause(self, where: Dict) -> Tuple[str, List]:
        if not where: return '1=1', []
        
        clauses, params = [], []
        for k, v in where.items():
            if v is None: clauses.append(f"{k} IS NULL")
            elif isinstance(v, list):
                clauses.append(f"{k} IN ({','.join(['%s']*len(v))})")
                params.extend(v)
            elif isinstance(v, tuple) and len(v) == 2:
                operator, value = v
                clauses.append(f"{k} {operator} %s")
                params.append(value)
            else:
                clauses.append(f"{k}=%s")
                params.append(v)
        return " AND ".join(clauses), params


    # 构建 SET 子句
    def _buildSetClause(self, setData: Dict) -> Tuple[str, List]:
        clauses, params = [], []
        for k, v in setData.items():
            clauses.append(f"{k}=%s")
            params.append(v)
        return ", ".join(clauses), params


    # 转换参数为可哈希类型以支持缓存
    def _convertToHashable(self, data: Any) -> Any:
        if isinstance(data, dict): return tuple(sorted(data.items()))
        elif isinstance(data, list): return tuple(data)
        return data    
    