SET search_path TO yy_uav;

-- 1. 查询当前可用无人机
SELECT * FROM drone WHERE status = '可用';

-- 2. 查询电量充足的可用电池
SELECT * FROM battery WHERE status = '可用' AND power_level >= 30;

-- 3. 查询全部巡检任务
SELECT 
    t.task_id,
    a.area_name,
    d.drone_code,
    b.battery_code,
    p.pilot_name,
    t.plan_start_time,
    t.plan_end_time,
    t.task_status
FROM inspection_task t
JOIN inspection_area a ON t.area_id = a.area_id
JOIN drone d ON t.drone_id = d.drone_id
JOIN battery b ON t.battery_id = b.battery_id
JOIN pilot p ON t.pilot_id = p.pilot_id
ORDER BY t.plan_start_time DESC;

-- 4. 查询待处理异常
SELECT * FROM abnormal_record WHERE status = '待处理';

-- 5. 检查无人机时间冲突示例
-- 假设想安排 UAV001 在 2026-05-04 15:10 到 15:40 执行新任务
SELECT *
FROM inspection_task
WHERE drone_id = 1
  AND task_status IN ('未开始', '执行中')
  AND plan_start_time < '2026-05-04 15:40:00'
  AND plan_end_time > '2026-05-04 15:10:00';
