SET search_path TO yy_uav;

INSERT INTO user_account(username, password, role, real_name, phone) VALUES
('admin', '123456', '管理员', '系统管理员', '13800000001'),
('pilot01', '123456', '飞手', '张飞', '13800000002'),
('repair01', '123456', '维修人员', '李工', '13800000003');

INSERT INTO drone(drone_code, model, max_flight_time, status, purchase_date, last_maintenance_date) VALUES
('UAV001', 'DJI Mavic 3E', 45, '可用', '2025-09-01', '2026-04-01'),
('UAV002', 'DJI Matrice 30T', 40, '可用', '2025-10-10', '2026-03-20'),
('UAV003', 'Autel EVO II', 38, '维修中', '2025-06-15', '2026-04-10'),
('UAV004', 'DJI Mini 4 Pro', 34, '可用', '2025-11-01', '2026-03-28'),
('UAV005', 'DJI Air 3', 42, '报废', '2024-10-01', '2026-02-18');

INSERT INTO battery(battery_code, drone_id, power_level, cycle_count, status) VALUES
('BAT001', 1, 85, 36, '可用'),
('BAT002', 1, 25, 55, '可用'),
('BAT003', 2, 90, 21, '可用'),
('BAT004', 2, 40, 60, '可用'),
('BAT005', 3, 70, 80, '可用'),
('BAT006', 4, 15, 40, '充电中'),
('BAT007', 4, 77, 18, '可用'),
('BAT008', 5, 10, 130, '报废');

INSERT INTO pilot(pilot_name, certificate_no, phone, skill_level, status) VALUES
('张飞', 'CAAC-UAV-001', '13811110001', '高级', '空闲'),
('王强', 'CAAC-UAV-002', '13811110002', '中级', '空闲'),
('赵明', 'CAAC-UAV-003', '13811110003', '初级', '休假'),
('刘洋', 'CAAC-UAV-004', '13811110004', '中级', '空闲'),
('陈晨', 'CAAC-UAV-005', '13811110005', '高级', '执行中');

INSERT INTO inspection_area(area_name, area_type, risk_level, inspection_cycle, description) VALUES
('图书馆屋顶', '建筑', '高', 7, '雨雪天气后重点检查排水口和屋面裂缝'),
('一号教学楼外立面', '建筑', '中', 14, '检查外墙脱落风险'),
('校园主干道', '道路', '中', 7, '检查道路破损和积水情况'),
('林区边界A段', '林区', '高', 3, '检查倒伏树木和火情隐患'),
('施工围挡区域', '施工区', '高', 2, '检查围挡稳定性和安全隐患'),
('消防通道东侧', '消防通道', '高', 5, '检查是否被车辆或杂物占用'),
('体育馆屋面', '建筑', '中', 10, '检查屋面板连接和排水情况'),
('光伏设备实验区', '光伏设备区', '中', 7, '检查组件破损、遮挡和支架稳定性');

INSERT INTO inspection_task(area_id, drone_id, battery_id, pilot_id, plan_start_time, plan_end_time, task_status) VALUES
(1, 1, 1, 1, '2026-05-01 09:00:00', '2026-05-01 09:40:00', '已完成'),
(3, 2, 3, 2, '2026-05-01 10:00:00', '2026-05-01 10:35:00', '已完成'),
(4, 4, 4, 4, '2026-05-02 14:00:00', '2026-05-02 14:30:00', '未开始'),
(6, 2, 4, 2, '2026-05-03 08:30:00', '2026-05-03 09:00:00', '未开始'),
(8, 1, 1, 1, '2026-05-04 15:00:00', '2026-05-04 15:30:00', '未开始');

INSERT INTO inspection_result(task_id, has_abnormal, result_description, upload_time) VALUES
(1, '是', '发现图书馆屋顶西侧排水口堵塞，有积水风险。', '2026-05-01 10:00:00'),
(2, '否', '校园主干道路面整体正常，未发现明显破损。', '2026-05-01 11:00:00');

INSERT INTO abnormal_record(task_id, abnormal_type, abnormal_level, location, description, status) VALUES
(1, '屋顶积水', '较重', '图书馆屋顶西侧', '排水口堵塞，雨后可能形成积水。', '待处理');

INSERT INTO maintenance_record(drone_id, maintenance_date, maintenance_content, maintenance_person, next_maintenance_date) VALUES
(1, '2026-04-01', '检查云台、电机和桨叶，状态正常。', '李工', '2026-05-01'),
(3, '2026-04-10', '发现电机异响，进入维修状态。', '李工', '2026-05-10');
