from flask import Blueprint, request
from app.controllers import iot_controller
from app.utils.responses import error_response, success_response

api_bp = Blueprint("api", __name__, url_prefix="/api")


def _json_body():
    return request.get_json(silent=True)


@api_bp.get("/health")
def health_check():
    return success_response({"service": "air-quality-iot-api", "status": "healthy"})


@api_bp.get("/zones")
def get_zones():
    data, err, code = iot_controller.list_zones()
    return error_response(err, code) if err else success_response(data, "Daftar zona.")


@api_bp.post("/zones")
def post_zone():
    data, err, code = iot_controller.create_zone(_json_body())
    return (
        error_response(err, code)
        if err
        else success_response(data, "Zona berhasil dibuat.", code)
    )


@api_bp.get("/nodes")
def get_nodes():
    data, err, code = iot_controller.list_nodes(request.args.get("zone_id"))
    return error_response(err, code) if err else success_response(data, "Daftar node.")


@api_bp.post("/nodes")
def post_node():
    data, err, code = iot_controller.create_node(_json_body())
    return (
        error_response(err, code)
        if err
        else success_response(data, "Node berhasil didaftarkan.", code)
    )


@api_bp.get("/readings")
def get_readings():
    data, err, code, meta = iot_controller.list_readings(
        node_id=request.args.get("node_id"),
        page=request.args.get("page", 1),
        per_page=request.args.get("per_page", 10),
    )
    return (
        error_response(err, code)
        if err
        else success_response(data, "Data telemetri sensor.", 200, meta=meta)
    )


@api_bp.post("/readings")
def post_reading():
    data, err, code = iot_controller.create_reading(_json_body())
    return (
        error_response(err, code)
        if err
        else success_response(data, "Data telemetri tersimpan.", code)
    )


@api_bp.get("/alerts")
def get_alerts():
    data, err, code = iot_controller.list_alerts(
        status=request.args.get("status"),
        zone_id=request.args.get("zone_id"),
    )
    return error_response(err, code) if err else success_response(data, "Daftar alert.")


@api_bp.patch("/alerts/<int:alert_id>/status")
def patch_alert_status(alert_id):
    data, err, code = iot_controller.update_alert_status(alert_id, _json_body())
    return (
        error_response(err, code)
        if err
        else success_response(data, "Status alert diperbarui.", code)
    )


@api_bp.get("/maintenance")
def get_maintenance():
    data, err, code = iot_controller.list_maintenance(request.args.get("node_id"))
    return (
        error_response(err, code)
        if err
        else success_response(data, "Riwayat maintenance node.")
    )


@api_bp.post("/maintenance")
def post_maintenance():
    data, err, code = iot_controller.create_maintenance(_json_body())
    return (
        error_response(err, code)
        if err
        else success_response(data, "Log maintenance tersimpan.", code)
    )