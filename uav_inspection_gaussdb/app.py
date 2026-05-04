import os
from flask import Flask, render_template, request, redirect, url_for, flash
from dotenv import load_dotenv
import psycopg2
import psycopg2.extras
from psycopg2 import sql

load_dotenv()

app = Flask(__name__)
app.secret_key = "uav-inspection-demo-key"


def get_conn():
    conn = psycopg2.connect(
        host=os.getenv("DB_HOST", "127.0.0.1"),
        port=os.getenv("DB_PORT", "5432"),
        dbname=os.getenv("DB_NAME", "teaching"),
        user=os.getenv("DB_USER", ""),
        password=os.getenv("DB_PASSWORD", ""),
        cursor_factory=psycopg2.extras.RealDictCursor
    )
    schema = os.getenv("DB_SCHEMA", "").strip()
    if schema:
        with conn.cursor() as cur:
            cur.execute(sql.SQL("SET search_path TO {}").format(sql.Identifier(schema)))
    return conn


def query_all(sql_text, params=None):
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(sql_text, params or ())
            return cur.fetchall()


def query_one(sql_text, params=None):
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(sql_text, params or ())
            return cur.fetchone()


def execute(sql_text, params=None):
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(sql_text, params or ())
        conn.commit()


@app.route("/")
def dashboard():
    data = {
        "today_tasks": query_one("""
            SELECT COUNT(*) AS count FROM inspection_task
            WHERE plan_start_time >= CURRENT_DATE
              AND plan_start_time < CURRENT_DATE + INTERVAL '1 day'
        """)["count"],
        "available_drones": query_one("SELECT COUNT(*) AS count FROM drone WHERE status='可用'")["count"],
        "available_batteries": query_one("""
            SELECT COUNT(*) AS count FROM battery
            WHERE status='可用' AND power_level >= 30
        """)["count"],
        "pending_abnormal": query_one("SELECT COUNT(*) AS count FROM abnormal_record WHERE status='待处理'")["count"],
        "finished_tasks": query_one("SELECT COUNT(*) AS count FROM inspection_task WHERE task_status='已完成'")["count"],
        "repairing_drones": query_one("SELECT COUNT(*) AS count FROM drone WHERE status='维修中'")["count"],
    }

    recent_tasks = query_all("""
        SELECT t.task_id, a.area_name, d.drone_code, p.pilot_name,
               t.plan_start_time, t.plan_end_time, t.task_status
        FROM inspection_task t
        JOIN inspection_area a ON t.area_id = a.area_id
        JOIN drone d ON t.drone_id = d.drone_id
        JOIN pilot p ON t.pilot_id = p.pilot_id
        ORDER BY t.plan_start_time DESC
        LIMIT 8
    """)
    return render_template("dashboard.html", data=data, recent_tasks=recent_tasks)


@app.route("/drones", methods=["GET", "POST"])
def drones():
    if request.method == "POST":
        execute("""
            INSERT INTO drone(drone_code, model, max_flight_time, status, purchase_date, last_maintenance_date)
            VALUES(%s, %s, %s, %s, %s, %s)
        """, (
            request.form["drone_code"],
            request.form["model"],
            request.form["max_flight_time"],
            request.form["status"],
            request.form.get("purchase_date") or None,
            request.form.get("last_maintenance_date") or None
        ))
        flash("无人机添加成功")
        return redirect(url_for("drones"))

    rows = query_all("SELECT * FROM drone ORDER BY drone_id")
    return render_template("drones.html", drones=rows)


@app.route("/drone/status/<int:drone_id>", methods=["POST"])
def update_drone_status(drone_id):
    execute("UPDATE drone SET status=%s WHERE drone_id=%s", (request.form["status"], drone_id))
    flash("无人机状态已更新")
    return redirect(url_for("drones"))


@app.route("/batteries", methods=["GET", "POST"])
def batteries():
    if request.method == "POST":
        execute("""
            INSERT INTO battery(battery_code, drone_id, power_level, cycle_count, status)
            VALUES(%s, %s, %s, %s, %s)
        """, (
            request.form["battery_code"],
            request.form.get("drone_id") or None,
            request.form["power_level"],
            request.form["cycle_count"],
            request.form["status"]
        ))
        flash("电池添加成功")
        return redirect(url_for("batteries"))

    rows = query_all("""
        SELECT b.*, d.drone_code
        FROM battery b
        LEFT JOIN drone d ON b.drone_id = d.drone_id
        ORDER BY b.battery_id
    """)
    drones = query_all("SELECT drone_id, drone_code FROM drone ORDER BY drone_id")
    return render_template("batteries.html", batteries=rows, drones=drones)


@app.route("/battery/status/<int:battery_id>", methods=["POST"])
def update_battery_status(battery_id):
    execute("""
        UPDATE battery SET status=%s, power_level=%s
        WHERE battery_id=%s
    """, (request.form["status"], request.form["power_level"], battery_id))
    flash("电池状态已更新")
    return redirect(url_for("batteries"))


@app.route("/areas", methods=["GET", "POST"])
def areas():
    if request.method == "POST":
        execute("""
            INSERT INTO inspection_area(area_name, area_type, risk_level, inspection_cycle, description)
            VALUES(%s, %s, %s, %s, %s)
        """, (
            request.form["area_name"],
            request.form["area_type"],
            request.form["risk_level"],
            request.form["inspection_cycle"],
            request.form.get("description")
        ))
        flash("巡检区域添加成功")
        return redirect(url_for("areas"))

    rows = query_all("SELECT * FROM inspection_area ORDER BY area_id")
    return render_template("areas.html", areas=rows)


@app.route("/tasks", methods=["GET", "POST"])
def tasks():
    if request.method == "POST":
        area_id = request.form["area_id"]
        drone_id = request.form["drone_id"]
        battery_id = request.form["battery_id"]
        pilot_id = request.form["pilot_id"]
        start_time = request.form["plan_start_time"].replace("T", " ")
        end_time = request.form["plan_end_time"].replace("T", " ")

        if end_time <= start_time:
            flash("结束时间必须晚于开始时间")
            return redirect(url_for("tasks"))

        drone = query_one("SELECT * FROM drone WHERE drone_id=%s", (drone_id,))
        if not drone or drone["status"] != "可用":
            flash("该无人机不是可用状态，不能安排任务")
            return redirect(url_for("tasks"))

        battery = query_one("SELECT * FROM battery WHERE battery_id=%s", (battery_id,))
        if not battery or battery["status"] != "可用" or battery["power_level"] < 30:
            flash("该电池不可用或电量低于30%，不能安排任务")
            return redirect(url_for("tasks"))

        pilot = query_one("SELECT * FROM pilot WHERE pilot_id=%s", (pilot_id,))
        if not pilot or pilot["status"] != "空闲":
            flash("该飞手不是空闲状态，不能安排任务")
            return redirect(url_for("tasks"))

        drone_conflict = query_one("""
            SELECT task_id FROM inspection_task
            WHERE drone_id=%s
              AND task_status IN ('未开始', '执行中')
              AND plan_start_time < %s
              AND plan_end_time > %s
            LIMIT 1
        """, (drone_id, end_time, start_time))
        if drone_conflict:
            flash(f"无人机时间冲突，已存在任务编号：{drone_conflict['task_id']}")
            return redirect(url_for("tasks"))

        pilot_conflict = query_one("""
            SELECT task_id FROM inspection_task
            WHERE pilot_id=%s
              AND task_status IN ('未开始', '执行中')
              AND plan_start_time < %s
              AND plan_end_time > %s
            LIMIT 1
        """, (pilot_id, end_time, start_time))
        if pilot_conflict:
            flash(f"飞手时间冲突，已存在任务编号：{pilot_conflict['task_id']}")
            return redirect(url_for("tasks"))

        execute("""
            INSERT INTO inspection_task(area_id, drone_id, battery_id, pilot_id, plan_start_time, plan_end_time, task_status)
            VALUES(%s, %s, %s, %s, %s, %s, '未开始')
        """, (area_id, drone_id, battery_id, pilot_id, start_time, end_time))
        flash("巡检任务添加成功")
        return redirect(url_for("tasks"))

    rows = query_all("""
        SELECT t.*, a.area_name, d.drone_code, b.battery_code, p.pilot_name
        FROM inspection_task t
        JOIN inspection_area a ON t.area_id = a.area_id
        JOIN drone d ON t.drone_id = d.drone_id
        JOIN battery b ON t.battery_id = b.battery_id
        JOIN pilot p ON t.pilot_id = p.pilot_id
        ORDER BY t.plan_start_time DESC
    """)
    areas = query_all("SELECT area_id, area_name FROM inspection_area ORDER BY area_id")
    drones = query_all("SELECT drone_id, drone_code, status FROM drone ORDER BY drone_id")
    batteries = query_all("SELECT battery_id, battery_code, power_level, status FROM battery ORDER BY battery_id")
    pilots = query_all("SELECT pilot_id, pilot_name, status FROM pilot ORDER BY pilot_id")

    return render_template("tasks.html", tasks=rows, areas=areas, drones=drones, batteries=batteries, pilots=pilots)


@app.route("/task/status/<int:task_id>", methods=["POST"])
def update_task_status(task_id):
    execute("UPDATE inspection_task SET task_status=%s WHERE task_id=%s", (request.form["task_status"], task_id))
    flash("任务状态已更新")
    return redirect(url_for("tasks"))


@app.route("/task/result/<int:task_id>", methods=["POST"])
def add_task_result(task_id):
    has_abnormal = request.form["has_abnormal"]
    result_description = request.form["result_description"]

    existed = query_one("SELECT result_id FROM inspection_result WHERE task_id=%s", (task_id,))
    if existed:
        execute("""
            UPDATE inspection_result
            SET has_abnormal=%s, result_description=%s, upload_time=CURRENT_TIMESTAMP
            WHERE task_id=%s
        """, (has_abnormal, result_description, task_id))
    else:
        execute("""
            INSERT INTO inspection_result(task_id, has_abnormal, result_description)
            VALUES(%s, %s, %s)
        """, (task_id, has_abnormal, result_description))

    execute("UPDATE inspection_task SET task_status='已完成', actual_end_time=CURRENT_TIMESTAMP WHERE task_id=%s", (task_id,))

    if has_abnormal == "是":
        execute("""
            INSERT INTO abnormal_record(task_id, abnormal_type, abnormal_level, location, description, status)
            VALUES(%s, %s, %s, %s, %s, '待处理')
        """, (
            task_id,
            request.form.get("abnormal_type") or "其他异常",
            request.form.get("abnormal_level") or "一般",
            request.form.get("location") or "未填写",
            result_description
        ))

    flash("巡检结果已提交")
    return redirect(url_for("tasks"))


@app.route("/abnormalities")
def abnormalities():
    rows = query_all("""
        SELECT ar.*, a.area_name, t.plan_start_time
        FROM abnormal_record ar
        JOIN inspection_task t ON ar.task_id = t.task_id
        JOIN inspection_area a ON t.area_id = a.area_id
        ORDER BY ar.abnormal_id DESC
    """)
    return render_template("abnormalities.html", abnormalities=rows)


@app.route("/repair/<int:abnormal_id>", methods=["POST"])
def add_repair(abnormal_id):
    execute("""
        INSERT INTO repair_record(abnormal_id, repair_person, repair_method, repair_result, review_status)
        VALUES(%s, %s, %s, %s, %s)
    """, (
        abnormal_id,
        request.form["repair_person"],
        request.form["repair_method"],
        request.form["repair_result"],
        request.form["review_status"]
    ))

    new_status = "已完成" if request.form["repair_result"] == "已完成" and request.form["review_status"] == "通过" else "处理中"
    execute("UPDATE abnormal_record SET status=%s WHERE abnormal_id=%s", (new_status, abnormal_id))

    flash("维修处理记录已添加")
    return redirect(url_for("abnormalities"))


if __name__ == "__main__":
    app.run(debug=True)
