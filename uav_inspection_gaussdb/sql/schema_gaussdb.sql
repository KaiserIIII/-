-- =========================================================
-- 高校园区无人机巡检任务管理系统数据库
-- 适配学校 GaussDB / openGauss / PostgreSQL
-- 注意：不要 CREATE DATABASE，直接在 teaching 数据库里运行本文件
-- =========================================================

CREATE SCHEMA IF NOT EXISTS yy_uav;
SET search_path TO yy_uav;

DROP TABLE IF EXISTS repair_record;
DROP TABLE IF EXISTS abnormal_record;
DROP TABLE IF EXISTS inspection_result;
DROP TABLE IF EXISTS inspection_task;
DROP TABLE IF EXISTS maintenance_record;
DROP TABLE IF EXISTS battery;
DROP TABLE IF EXISTS drone;
DROP TABLE IF EXISTS pilot;
DROP TABLE IF EXISTS inspection_area;
DROP TABLE IF EXISTS user_account;

CREATE TABLE user_account (
    user_id SERIAL PRIMARY KEY,
    username VARCHAR(30) NOT NULL UNIQUE,
    password VARCHAR(100) NOT NULL,
    role VARCHAR(20) NOT NULL CHECK (role IN ('管理员', '飞手', '维修人员')),
    real_name VARCHAR(30) NOT NULL,
    phone VARCHAR(20)
);

CREATE TABLE drone (
    drone_id SERIAL PRIMARY KEY,
    drone_code VARCHAR(20) NOT NULL UNIQUE,
    model VARCHAR(50) NOT NULL,
    max_flight_time INT NOT NULL CHECK (max_flight_time > 0),
    status VARCHAR(20) NOT NULL CHECK (status IN ('可用', '使用中', '维修中', '报废')),
    purchase_date DATE,
    last_maintenance_date DATE
);

CREATE TABLE battery (
    battery_id SERIAL PRIMARY KEY,
    battery_code VARCHAR(20) NOT NULL UNIQUE,
    drone_id INT REFERENCES drone(drone_id),
    power_level INT NOT NULL CHECK (power_level BETWEEN 0 AND 100),
    cycle_count INT DEFAULT 0 CHECK (cycle_count >= 0),
    status VARCHAR(20) NOT NULL CHECK (status IN ('可用', '充电中', '损坏', '报废'))
);

CREATE TABLE pilot (
    pilot_id SERIAL PRIMARY KEY,
    pilot_name VARCHAR(30) NOT NULL,
    certificate_no VARCHAR(50) NOT NULL UNIQUE,
    phone VARCHAR(20),
    skill_level VARCHAR(20) CHECK (skill_level IN ('初级', '中级', '高级')),
    status VARCHAR(20) NOT NULL CHECK (status IN ('空闲', '执行中', '休假'))
);

CREATE TABLE inspection_area (
    area_id SERIAL PRIMARY KEY,
    area_name VARCHAR(100) NOT NULL,
    area_type VARCHAR(30) NOT NULL,
    risk_level VARCHAR(10) CHECK (risk_level IN ('低', '中', '高')),
    inspection_cycle INT NOT NULL CHECK (inspection_cycle > 0),
    description TEXT
);

CREATE TABLE inspection_task (
    task_id SERIAL PRIMARY KEY,
    area_id INT NOT NULL REFERENCES inspection_area(area_id),
    drone_id INT NOT NULL REFERENCES drone(drone_id),
    battery_id INT NOT NULL REFERENCES battery(battery_id),
    pilot_id INT NOT NULL REFERENCES pilot(pilot_id),
    plan_start_time TIMESTAMP NOT NULL,
    plan_end_time TIMESTAMP NOT NULL,
    actual_start_time TIMESTAMP,
    actual_end_time TIMESTAMP,
    task_status VARCHAR(20) NOT NULL CHECK (task_status IN ('未开始', '执行中', '已完成', '已取消')),
    CHECK (plan_end_time > plan_start_time)
);

CREATE TABLE inspection_result (
    result_id SERIAL PRIMARY KEY,
    task_id INT NOT NULL UNIQUE REFERENCES inspection_task(task_id),
    has_abnormal VARCHAR(5) NOT NULL CHECK (has_abnormal IN ('是', '否')),
    result_description TEXT,
    upload_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE abnormal_record (
    abnormal_id SERIAL PRIMARY KEY,
    task_id INT NOT NULL REFERENCES inspection_task(task_id),
    abnormal_type VARCHAR(30) NOT NULL,
    abnormal_level VARCHAR(20) NOT NULL CHECK (abnormal_level IN ('一般', '较重', '严重')),
    location VARCHAR(100),
    description TEXT,
    status VARCHAR(20) NOT NULL CHECK (status IN ('待处理', '处理中', '已完成'))
);

CREATE TABLE repair_record (
    repair_id SERIAL PRIMARY KEY,
    abnormal_id INT NOT NULL REFERENCES abnormal_record(abnormal_id),
    repair_person VARCHAR(30) NOT NULL,
    repair_method TEXT,
    repair_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    repair_result VARCHAR(20) NOT NULL CHECK (repair_result IN ('已完成', '未完成')),
    review_status VARCHAR(20) CHECK (review_status IN ('通过', '未通过'))
);

CREATE TABLE maintenance_record (
    maintenance_id SERIAL PRIMARY KEY,
    drone_id INT NOT NULL REFERENCES drone(drone_id),
    maintenance_date DATE NOT NULL,
    maintenance_content TEXT,
    maintenance_person VARCHAR(30),
    next_maintenance_date DATE
);

-- 索引设计：提高任务查询、冲突检查、异常处理的速度
CREATE INDEX idx_task_drone_time ON inspection_task(drone_id, plan_start_time, plan_end_time);
CREATE INDEX idx_task_pilot_time ON inspection_task(pilot_id, plan_start_time, plan_end_time);
CREATE INDEX idx_task_status ON inspection_task(task_status);
CREATE INDEX idx_abnormal_status ON abnormal_record(status);
CREATE INDEX idx_battery_power ON battery(power_level);
