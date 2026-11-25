# Multi-Zone Environmental & Air Quality Monitoring REST API

Proyek MVP REST API berbasis **Python Flask**, **Flask-SQLAlchemy (ORM)**, dan arsitektur **MVC** untuk pemantauan kualitas udara dan kondisi lingkungan lintas zona pada domain **Internet of Things (IoT)**.

## Fitur Utama (MVP)
- **Manajemen Zona (`zones`)**: Pengelolaan data zona pemantauan beserta ambang batas maksimum (`temp_max`, `humidity_max`, `air_quality_max`).
- **Manajemen Node Sensor (`nodes`)**: Pendaftaran dan daftar *node* perangkat dengan dukungan *filter* `zone_id`.
- **Pencatatan Telemetri & Evaluasi Batas (`sensor_readings`)**: Penyimpanan pembacaan suhu, kelembapan, dan `air_quality_ppm` dengan *pagination* (`page`, `per_page`) serta pemicu otomatis *alert* bila melewati ambang batas zona.
- **Manajemen Alert (`air_quality_alerts`)**: Daftar *alert* (mendukung *filter* `status` dan `zone_id`) serta pembaruan status (`open`, `acknowledged`, `resolved`).
- **Riwayat Perawatan Node (`maintenance_logs`)**: Pencatatan aktivitas `calibration`, `repair`, atau `inspection` per *node*.

## Struktur Folder (MVC)
```text
air-quality-iot-api/
├── app/
│   ├── __init__.py
│   ├── config.py
│   ├── controllers/
│   │   └── iot_controller.py
│   ├── models/
│   │   └── models.py
│   ├── routes/
│   │   └── api_routes.py
│   └── utils/
│       ├── responses.py
│       └── seed.py
├── postman/
│   └── air_quality_api.json
├── tests/
│   └── test_api.py
├── .gitignore
├── requirements.txt
├── run.py
└── README.md