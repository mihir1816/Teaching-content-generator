from flask import Blueprint
from controllers.plan_controller import generate_plan_controller

plan_bp = Blueprint("plan_bp", __name__)

# POST /api/plan/generate
plan_bp.route("/generate", methods=["POST"])(generate_plan_controller)
