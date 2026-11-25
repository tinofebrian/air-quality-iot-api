from datetime import datetime, timezone
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def utc_now():
    return datetime.now(timezone.utc)


class Zone(db.Model):
    __tablename__ = "zones"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    location_code = db.Column(db.String(30), unique=True, nullable=False)
    temp_max = db.Column(db.Float, nullable=False, default=30.0)
    humidity_max = db.Column(db.Float, nullable=False, default=75.0)
    air_quality_max = db.Column(db.Float, nullable=False, default=100.0)
    created_at = db.Column(db.DateTime, default=utc_now, nullable=False)

    nodes = db.relationship("Node", back_populates="zone", cascade="all, delete-orphan")
    alerts = db.relationship(
        "AirQualityAlert", back_populates="zone", cascade="all, delete-orphan"
    )

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "location_code": self.location_code,
            "temp_max": self.temp_max,
            "humidity_max": self.humidity_max,
            "air_quality_max": self.air_quality_max,
            "created_at": self.created_at.isoformat(),
        }


class Node(db.Model):
    __tablename__ = "nodes"

    id = db.Column(db.Integer, primary_key=True)
    zone_id = db.Column(db.Integer, db.ForeignKey("zones.id"), nullable=False)
    device_code = db.Column(db.String(50), unique=True, nullable=False)
    model_name = db.Column(db.String(80), nullable=False)
    status = db.Column(db.String(20), nullable=False, default="active")
    last_seen_at = db.Column(db.DateTime, default=utc_now, nullable=False)

    zone = db.relationship("Zone", back_populates="nodes")
    readings = db.relationship(
        "SensorReading", back_populates="node", cascade="all, delete-orphan"
    )
    alerts = db.relationship(
        "AirQualityAlert", back_populates="node", cascade="all, delete-orphan"
    )
    maintenance_logs = db.relationship(
        "MaintenanceLog", back_populates="node", cascade="all, delete-orphan"
    )

    def to_dict(self):
        return {
            "id": self.id,
            "zone_id": self.zone_id,
            "device_code": self.device_code,
            "model_name": self.model_name,
            "status": self.status,
            "last_seen_at": self.last_seen_at.isoformat(),
        }


class SensorReading(db.Model):
    __tablename__ = "sensor_readings"

    id = db.Column(db.Integer, primary_key=True)
    node_id = db.Column(db.Integer, db.ForeignKey("nodes.id"), nullable=False)
    temperature = db.Column(db.Float, nullable=False)
    humidity = db.Column(db.Float, nullable=False)
    air_quality_ppm = db.Column(db.Float, nullable=False)
    recorded_at = db.Column(db.DateTime, default=utc_now, nullable=False)

    node = db.relationship("Node", back_populates="readings")

    def to_dict(self):
        return {
            "id": self.id,
            "node_id": self.node_id,
            "temperature": self.temperature,
            "humidity": self.humidity,
            "air_quality_ppm": self.air_quality_ppm,
            "recorded_at": self.recorded_at.isoformat(),
        }


class AirQualityAlert(db.Model):
    __tablename__ = "air_quality_alerts"

    id = db.Column(db.Integer, primary_key=True)
    zone_id = db.Column(db.Integer, db.ForeignKey("zones.id"), nullable=False)
    node_id = db.Column(db.Integer, db.ForeignKey("nodes.id"), nullable=False)
    metric_name = db.Column(db.String(30), nullable=False)
    measured_value = db.Column(db.Float, nullable=False)
    threshold_value = db.Column(db.Float, nullable=False)
    severity = db.Column(db.String(20), nullable=False, default="warning")
    status = db.Column(db.String(20), nullable=False, default="open")
    created_at = db.Column(db.DateTime, default=utc_now, nullable=False)

    zone = db.relationship("Zone", back_populates="alerts")
    node = db.relationship("Node", back_populates="alerts")

    def to_dict(self):
        return {
            "id": self.id,
            "zone_id": self.zone_id,
            "node_id": self.node_id,
            "metric_name": self.metric_name,
            "measured_value": self.measured_value,
            "threshold_value": self.threshold_value,
            "severity": self.severity,
            "status": self.status,
            "created_at": self.created_at.isoformat(),
        }


class MaintenanceLog(db.Model):
    __tablename__ = "maintenance_logs"

    id = db.Column(db.Integer, primary_key=True)
    node_id = db.Column(db.Integer, db.ForeignKey("nodes.id"), nullable=False)
    activity_type = db.Column(db.String(30), nullable=False)
    notes = db.Column(db.Text, nullable=False)
    performed_by = db.Column(db.String(100), nullable=False)
    performed_at = db.Column(db.DateTime, default=utc_now, nullable=False)

    node = db.relationship("Node", back_populates="maintenance_logs")

    def to_dict(self):
        return {
            "id": self.id,
            "node_id": self.node_id,
            "activity_type": self.activity_type,
            "notes": self.notes,
            "performed_by": self.performed_by,
            "performed_at": self.performed_at.isoformat(),
        }