from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from typing import List, Dict, Any

def get_verification_failed_keyboard() -> InlineKeyboardMarkup:
    keyboard = [
        [
            InlineKeyboardButton("🔄 Try Again", callback_data="action_try_again"),
            InlineKeyboardButton("❌ Cancel", callback_data="action_cancel")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_reports_list_keyboard(reports: List[Dict[str, Any]]) -> InlineKeyboardMarkup:
    keyboard = []
    for idx, r in enumerate(reports, 1):
        report_id = r.get("reportId", "N/A")
        scan_type = r.get("scanType", "Scan")
        date_str = r.get("formattedDate", "")
        
        btn_text = f"{idx}. {report_id} | {scan_type}"
        if date_str:
            btn_text += f" | {date_str}"
            
        keyboard.append([InlineKeyboardButton(btn_text, callback_data=f"report_select:{report_id}")])
        
    keyboard.append([InlineKeyboardButton("🚪 Exit Session", callback_data="action_exit")])
    return InlineKeyboardMarkup(keyboard)

def get_report_action_keyboard(report_id: str) -> InlineKeyboardMarkup:
    keyboard = [
        [
            InlineKeyboardButton("📥 Download PDF", callback_data=f"pdf_download:{report_id}")
        ],
        [
            InlineKeyboardButton("⬅️ Back to Reports", callback_data="action_back_to_reports"),
            InlineKeyboardButton("🚪 Exit", callback_data="action_exit")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)
