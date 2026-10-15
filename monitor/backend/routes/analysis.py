from datetime import datetime

from flask import Blueprint, jsonify, request

from learning.report import build_report
from learning.support import current_boundary, first_reference_time, read_observation
from routes.auth import login_required

analysis = Blueprint("analysis", __name__)


@analysis.post("/api/analysis/start")
@login_required
def start_observation():
    return jsonify(after_id=current_boundary())


@analysis.get("/api/analysis")
@login_required
def get_analysis():
    after_text = request.args.get("after_id", "")
    threshold_text = request.args.get("threshold", "10")
    if not after_text.isdecimal() or not threshold_text.isdecimal():
        return jsonify(message="시작 ID와 기준은 숫자여야 합니다."), 400
    after_id, threshold = int(after_text), int(threshold_text)
    if after_id < 0 or not 1 <= threshold <= 1000:
        return jsonify(message="시작 ID 또는 기준 범위가 올바르지 않습니다."), 400

    reference_text = request.args.get("reference_time")
    if reference_text:
        try:
            reference_time = datetime.fromisoformat(reference_text)
            if reference_time.tzinfo is None or reference_time.utcoffset() is None:
                raise ValueError("timezone required")
        except ValueError:
            return jsonify(message="기준시각은 시간대가 포함된 ISO 시각이어야 합니다."), 400
    else:
        reference_time = first_reference_time()

    rows = read_observation(after_id, reference_time)
    return jsonify(build_report(rows, threshold, after_id, reference_time))
