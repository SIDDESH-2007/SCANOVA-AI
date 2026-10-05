from fastapi import APIRouter, Depends
from typing import Dict, Any
from app.api.auth import get_current_user
from app.database.mongodb import get_database

router = APIRouter()

@router.get("/summary", response_model=Dict[str, Any])
async def get_analytics_summary(current_user = Depends(get_current_user)):
    db = get_database()
    user_id_str = current_user.get("userId") or str(current_user.get("_id", ""))
    user_id_obj = current_user.get("_id")
    user_query = {"$in": [user_id_str, user_id_obj]}
    # 1. Scan Type Distribution
    scan_types = ["X-RAY", "CT", "MRI", "ULTRASOUND"]
    scanTypeDistribution = []
    for stype in scan_types:
        count = await db.scans.count_documents({"userId": user_query, "scanType": stype})
        scanTypeDistribution.append({"name": stype, "value": count})
        
    # 2. Daily Scan Trend (Basic aggregation grouped by day)
    pipeline_daily = [
        {"$match": {"userId": user_query}},
        {"$project": {"dateStr": {"$dateToString": {"format": "%Y-%m-%d", "date": "$uploadedAt"}}}},
        {"$group": {"_id": "$dateStr", "count": {"$sum": 1}}},
        {"$sort": {"_id": 1}},
        {"$limit": 7}
    ]
    daily_cursor = db.scans.aggregate(pipeline_daily)
    daily_raw = await daily_cursor.to_list(length=7)
    dailyScanTrend = [{"date": d["_id"], "scans": d["count"]} for d in daily_raw]
    if not dailyScanTrend:
        dailyScanTrend = [{"date": "No Data", "scans": 0}]

    # 3. Weekly Scan Trend
    pipeline_weekly = [
        {"$match": {"userId": user_query}},
        {"$project": {"yearWeek": {"$dateToString": {"format": "%Y-W%V", "date": "$uploadedAt"}}}},
        {"$group": {"_id": "$yearWeek", "count": {"$sum": 1}}},
        {"$sort": {"_id": 1}},
        {"$limit": 4}
    ]
    weekly_cursor = db.scans.aggregate(pipeline_weekly)
    weekly_raw = await weekly_cursor.to_list(length=4)
    weeklyScanTrend = [{"week": w["_id"], "scans": w["count"]} for w in weekly_raw]
    if not weeklyScanTrend:
        weeklyScanTrend = [{"week": "No Data", "scans": 0}]

    # 4. Monthly Scan Trend
    pipeline_monthly = [
        {"$match": {"userId": user_query}},
        {"$project": {"yearMonth": {"$dateToString": {"format": "%Y-%m", "date": "$uploadedAt"}}}},
        {"$group": {"_id": "$yearMonth", "count": {"$sum": 1}}},
        {"$sort": {"_id": 1}},
        {"$limit": 6}
    ]
    monthly_cursor = db.scans.aggregate(pipeline_monthly)
    monthly_raw = await monthly_cursor.to_list(length=6)
    monthlyScanTrend = [{"month": m["_id"], "scans": m["count"]} for m in monthly_raw]
    if not monthlyScanTrend:
        monthlyScanTrend = [{"month": "No Data", "scans": 0}]

    # 5. Finding Distribution
    pipeline_finding = [
        {"$match": {"userId": user_query}},
        {"$group": {"_id": "$possibleFinding", "count": {"$sum": 1}}}
    ]
    finding_cursor = db.predictions.aggregate(pipeline_finding)
    finding_raw = await finding_cursor.to_list(length=10)
    findingDistribution = [{"name": f["_id"] or "Unknown", "value": f["count"]} for f in finding_raw]
    if not findingDistribution:
        findingDistribution = [{"name": "No Data", "value": 0}]

    # 5. Review Status Distribution
    pipeline_review = [
        {"$match": {"userId": user_query}},
        {"$group": {"_id": "$reviewStatus", "count": {"$sum": 1}}}
    ]
    review_cursor = db.predictions.aggregate(pipeline_review)
    review_raw = await review_cursor.to_list(length=10)
    reviewStatusDistribution = [{"name": r["_id"] or "Pending", "value": r["count"]} for r in review_raw]
    if not reviewStatusDistribution:
        reviewStatusDistribution = [{"name": "No Data", "value": 0}]

    # 6. Emergency vs Normal
    emergency_count = await db.emergency_cases.count_documents({"userId": user_query})
    normal_count = await db.scans.count_documents({"userId": user_query, "caseType": "NORMAL"})
    emergencyVsNormal = [
        {"name": "Emergency", "value": emergency_count},
        {"name": "Normal", "value": normal_count}
    ]

    # 7. Confidence Distribution
    pipeline_conf = [
        {"$match": {"userId": user_query}},
        {"$group": {"_id": "$confidenceLevel", "count": {"$sum": 1}}}
    ]
    conf_cursor = db.predictions.aggregate(pipeline_conf)
    conf_raw = await conf_cursor.to_list(length=10)
    confidenceDistribution = [{"name": c["_id"] or "Unknown", "value": c["count"]} for c in conf_raw]
    if not confidenceDistribution:
        confidenceDistribution = [{"name": "No Data", "value": 0}]

    return {
        "scanTypeDistribution": scanTypeDistribution,
        "dailyScanTrend": dailyScanTrend,
        "weeklyScanTrend": weeklyScanTrend,
        "monthlyScanTrend": monthlyScanTrend,
        "findingDistribution": findingDistribution,
        "reviewStatusDistribution": reviewStatusDistribution,
        "emergencyVsNormal": emergencyVsNormal,
        "confidenceDistribution": confidenceDistribution
    }
