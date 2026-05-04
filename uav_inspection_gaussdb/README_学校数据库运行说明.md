# 高校园区无人机巡检任务管理系统

## 一、使用的学校数据库连接也要使用校园内网


- 主机：222.27.161.245
- 端口：15432
- 数据库：teaching


## 二、在 DBeaver 里建表

1. 连接学校 GaussDB。
2. 新建 SQL 编辑器。
3. 运行 `schema_gaussdb.sql`。
4. 再运行 `seed_gaussdb.sql`。
5. 可运行 `test_queries.sql` 检查数据。


## 三、在 PyCharm 编辑器编写里编写并运行

1. 打开本项目文件夹。
2. 把 `.env` 里的用户名、密码改成你的学校数据库账号。

示例：

```env
DB_HOST=222.27.161.245
DB_PORT=15432
DB_NAME=teaching
DB_USER=S你的学号
DB_PASSWORD=你的数据库密码
DB_SCHEMA=yy_uav
```


3. 浏览器打开：

```text
http://127.0.0.1:5000
```


