from sqlalchemy.exc import IntegrityError
from app.models.models import (
    AirQualityAlert,
    MaintenanceLog,
    Node,
    SensorReading,
    Zone,
    db,
    utc_now,
)


def list_zones():
    zones = Zone.query.order_by(Zone.id.asc()).all()
    return [z.to_dict() for z in zones], None, 200


def create_zone(payload):
    if not isinstance(payload, dict):
        return None, "Payload JSON wajib berupa objek.", 400

    name = (payload.get("name") or "").strip()
    location_code = (payload.get("location_code") or "").strip()
    if not name or not location_code:
        return None, "Field 'name' dan 'location_code' wajib diisi.", 400

    for field in ("temp_max", "humidity_max", "air_quality_max"):
        if field in payload and payload[field] is not None:
            try:
                val = float(payload[field])
                if val <= 0:
                    return None, f"Field '{field}' harus lebih besar dari 0.", 400
            except (TypeError, ValueError):
                return None, f"Field '{field}' harus berupa angka.", 400

    zone = Zone(
        name=name,
        location_code=location_code,
        temp_max=float(payload.get("temp_max", 30.0)),
        humidity_max=float(payload.get("humidity_max", 75.0)),
        air_quality_max=float(payload.get("air_quality_max", 100.0)),
    )
    try:
        db.session.add(zone)
        db.session.commit()
        return zone.to_dict(), None, 201
    except IntegrityError:
        db.session.rollback()
        return None, "location_code sudah terdaftar.", 400


def list_nodes(zone_id=None):
    query = Node.query
    if zone_id is not None:
        try:
            query = query.filter_by(zone_id=int(zone_id))
        except ValueError:
            return None, "Parameter 'zone_id' harus berupa integer.", 400
    nodes = query.order_by(Node.id.asc()).all()
    return [n.to_dict() for n in nodes], None, 200


def create_node(payload):
    if not isinstance(payload, dict):
        return None, "Payload JSON wajib berupa objek.", 400

    zone_id = payload.get("zone_id")
    device_code = (payload.get("device_code") or "").strip()
    model_name = (payload.get("model_name") or "").strip()
    status = (payload.get("status") or "active").strip().lower()

    if not zone_id or not device_code or not model_name:
        return None, "Field 'zone_id', 'device_code', dan 'model_name' wajib diisi.", 400

    if status not in ("active", "offline", "maintenance"):
        return None, "Status node harus salah satu dari: active, offline, maintenance.", 400

    zone = db.session.get(Zone, zone_id)
    if not zone:
        return None, "Zone tidak ditemukan.", 404

    node = Node(
        zone_id=zone.id,
        device_code=device_code,
        model_name=model_name,
        status=status,
    )
    try:
        db.session.add(node)
        db.session.commit()
        return node.to_dict(), None, 201
    except IntegrityError:
        db.session.rollback()
        return None, "device_code sudah terdaftar.", 400


def list_readings(node_id=None, page=1, per_page=10):
    try:
        page = max(1, int(page))
        per_page = min(100, max(1, int(per_page)))
    except ValueError:
        return None, "Parameter 'page' dan 'per_page' harus berupa integer.", 400, None

    query = SensorReading.query
    if node_id is not None:
        try:
            query = query.filter_by(node_id=int(node_id))
        except ValueError:
            return None, "Parameter 'node_id' harus berupa integer.", 400, None

    pagination = query.order_by(SensorReading.id.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    meta = {
        "page": pagination.page,
        "per_page": pagination.per_page,
        "total_items": pagination.total,
        "total_pages": pagination.pages,
    }
    return [r.to_dict() for r in pagination.items], None, 200, meta


def create_reading(payload):
    if not isinstance(payload, dict):
        return None, "Payload JSON wajib berupa objek.", 400

    required = ("node_id", "temperature", "humidity", "air_quality_ppm")
    if any(payload.get(k) is None for k in required):
        return (
            None,
            "Field 'node_id', 'temperature', 'humidity', dan 'air_quality_ppm' wajib diisi.",
            400,
        )

    try:
        node_id = int(payload["node_id"])
        temperature = float(payload["temperature"])
        humidity = float(payload["humidity"])
        air_quality_ppm = float(payload["air_quality_ppm"])
    except (TypeError, ValueError):
        return None, "Nilai sensor dan node_id harus berupa angka valid.", 400

    if not (0 <= humidity <= 100) or air_quality_ppm < 0:
        return None, "Nilai humidity harus 0-100 dan air_quality_ppm tidak boleh negatif.", 400

    node = db.session.get(Node, node_id)
    if not node:
        return None, "Node tidak ditemukan.", 404

    reading = SensorReading(
        node_id=node.id,
        temperature=temperature,
        humidity=humidity,
        air_quality_ppm=air_quality_ppm,
    )
    node.last_seen_at = utc_now()
    db.session.add(reading)

    zone = db.session.get(Zone, node.zone_id)
    created_alerts = []
    if zone:
        checks = [
            ("temperature", temperature, zone.temp_max),
            ("humidity", humidity, zone.humidity_max),
            ("air_quality_ppm", air_quality_ppm, zone.air_quality_max),
        ]
        for metric_name, measured, threshold in checks:
            if measured > threshold:
                severity = "critical" if measured > threshold * 1.25 else "warning"
                alert = AirQualityAlert(
                    zone_id=zone.id,
                    node_id=node.id,
                    metric_name=metric_name,
                    measured_value=measured,
                    threshold_value=threshold,
                    severity=severity,
                    status="open",
                )
                db.session.add(alert)
                created_alerts.append(alert)

    db.session.commit()
    result = reading.to_dict()
    result["triggered_alerts"] = [a.to_dict() for a in created_alerts]
    return result, None, 201


def list_alerts(status=None, zone_id=None):
    query = AirQualityAlert.query
    if status:
        query = query.filter_by(status=status.strip().lower())
    if zone_id is not None:
        try:
            query = query.filter_by(zone_id=int(zone_id))
        except ValueError:
            return None, "Parameter 'zone_id' harus berupa integer.", 400
    alerts = query.order_by(AirQualityAlert.id.desc()).all()
    return [a.to_dict() for a in alerts], None, 200


def update_alert_status(alert_id, payload):
    if not isinstance(payload, dict):
        return None, "Payload JSON wajib berupa objek.", 400

    new_status = (payload.get("status") or "").strip().lower()
    if new_status not in ("open", "acknowledged", "resolved"):
        return None, "Status alert harus salah satu dari: open, acknowledged, resolved.", 400

    alert = db.session.get(AirQualityAlert, alert_id)
    if not alert:
        return None, "Alert tidak ditemukan.", 404

    alert.status = new_status
    db.session.commit()
    return alert.to_dict(), None, 200


def list_maintenance(node_id=None):
    query = MaintenanceLog.query
    if node_id is not None:
        try:
            query = query.filter_by(node_id=int(node_id))
        except ValueError:
            return None, "Parameter 'node_id' harus berupa integer.", 400
    logs = query.order_by(MaintenanceLog.id.desc()).all()
    return [m.to_dict() for m in logs], None, 200


def create_maintenance(payload):
    if not isinstance(payload, dict):
        return None, "Payload JSON wajib berupa objek.", 400

    node_id = payload.get("node_id")
    activity_type = (payload.get("activity_type") or "").strip().lower()
    notes = (payload.get("notes") or "").strip()
    performed_by = (payload.get("performed_by") or "").strip()

    if not node_id or not activity_type or not notes or not performed_by:
        return (
            None,
            "Field 'node_id', 'activity_type', 'notes', dan 'performed_by' wajib diisi.",
            400,
        )

    if activity_type not in ("calibration", "repair", "inspection"):
        return (
            None,
            "activity_type harus salah satu dari: calibration, repair, inspection.",
            400,
        )

    try:
        node = db.session.get(Node, int(node_id))
    except (TypeError, ValueError):
        return None, "Field 'node_id' harus berupa integer.", 400

    if not node:
        return None, "Node tidak ditemukan.", 404

    log = MaintenanceLog(
        node_id=node.id,
        activity_type=activity_type,
        notes=notes,
        performed_by=performed_by,
    )
    db.session.add(log)
    db.session.commit()
    return log.to_dict(), None, 201