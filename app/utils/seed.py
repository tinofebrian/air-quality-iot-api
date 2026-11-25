from app.models.models import (
    AirQualityAlert,
    MaintenanceLog,
    Node,
    SensorReading,
    Zone,
    db,
)


def seed_database():
    if Zone.query.first() is not None:
        return

    z1 = Zone(
        name="Ruang Server Utama",
        location_code="ZN-SRV-01",
        temp_max=27.0,
        humidity_max=65.0,
        air_quality_max=80.0,
    )
    z2 = Zone(
        name="Laboratorium Riset",
        location_code="ZN-LAB-02",
        temp_max=29.0,
        humidity_max=70.0,
        air_quality_max=100.0,
    )
    db.session.add_all([z1, z2])
    db.session.flush()

    n1 = Node(
        zone_id=z1.id,
        device_code="ESP32-AQ-101",
        model_name="ESP32 + MQ135 + DHT22",
        status="active",
    )
    n2 = Node(
        zone_id=z2.id,
        device_code="ESP32-AQ-102",
        model_name="ESP32 + PMS5003 + DHT22",
        status="active",
    )
    db.session.add_all([n1, n2])
    db.session.flush()

    r1 = SensorReading(
        node_id=n1.id, temperature=25.4, humidity=55.0, air_quality_ppm=62.0
    )
    r2 = SensorReading(
        node_id=n2.id, temperature=31.2, humidity=68.0, air_quality_ppm=118.0
    )
    db.session.add_all([r1, r2])

    a1 = AirQualityAlert(
        zone_id=z2.id,
        node_id=n2.id,
        metric_name="air_quality_ppm",
        measured_value=118.0,
        threshold_value=100.0,
        severity="warning",
        status="open",
    )
    db.session.add(a1)

    m1 = MaintenanceLog(
        node_id=n1.id,
        activity_type="calibration",
        notes="Kalibrasi sensor MQ135 menggunakan udara bersih referensi.",
        performed_by="Teknisi IoT",
    )
    db.session.add(m1)
    db.session.commit()