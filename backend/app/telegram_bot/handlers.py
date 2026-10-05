import os
import logging
from datetime import datetime
from typing import Optional
from telegram import Update, InlineKeyboardMarkup
from telegram.ext import (
    ContextTypes,
    ConversationHandler,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters
)

from app.utils.phone_utils import normalize_patient_id, normalize_phone_number
from app.telegram_bot.states import WAITING_FOR_PATIENT_ID, WAITING_FOR_PHONE, SESSION_TIMEOUT_SECONDS
from app.telegram_bot.keyboards import (
    get_verification_failed_keyboard,
    get_reports_list_keyboard,
    get_report_action_keyboard
)
from app.telegram_bot.services import (
    verify_patient,
    get_patient_reports,
    get_report_details,
    get_report_pdf_path
)

logger = logging.getLogger(__name__)

def check_and_get_verified_patient_id(context: ContextTypes.DEFAULT_TYPE) -> Optional[str]:
    user_data = context.user_data
    patient_id = user_data.get("patient_id")
    verified_at = user_data.get("verified_at")
    
    if not patient_id or not verified_at:
        return None
        
    now = datetime.utcnow().timestamp()
    if (now - verified_at) > SESSION_TIMEOUT_SECONDS:
        logger.info(f"Session expired for patientId '{patient_id}'")
        user_data.clear()
        return None
        
    # Refresh activity timestamp
    user_data["verified_at"] = now
    return patient_id

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    logger.info(f"/start received from chat {update.effective_chat.id}")
    
    verified_pid = check_and_get_verified_patient_id(context)
    if verified_pid:
        patient_name = context.user_data.get("patient_name", "Patient")
        reports = await get_patient_reports(verified_pid)
        if not reports:
            await update.message.reply_text("No reports are currently available for this patient.")
        else:
            kb = get_reports_list_keyboard(reports)
            await update.message.reply_text(
                f"✅ Verified Session Active\n\nPatient ID: {verified_pid}\nName: {patient_name}\n\nAvailable Reports:",
                reply_markup=kb
            )
        return ConversationHandler.END

    context.user_data.clear()
    welcome_text = (
        "Welcome to the AI Diagnosis Report Bot.\n\n"
        "To access your medical imaging report, please verify your details.\n\n"
        "Please enter your Patient ID."
    )
    await update.message.reply_text(welcome_text)
    return WAITING_FOR_PATIENT_ID

async def handle_patient_id(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    raw_pid = update.message.text
    pid_input = normalize_patient_id(raw_pid)
    if not pid_input:
        await update.message.reply_text("Please enter a valid Patient ID.")
        return WAITING_FOR_PATIENT_ID

    context.user_data["temp_patient_id"] = pid_input
    logger.info(f"Patient ID entered: '{pid_input}' (raw: '{raw_pid}')")

    reply_text = (
        "Please enter your registered phone number.\n\n"
        "Example: +919876543210"
    )
    await update.message.reply_text(reply_text)
    return WAITING_FOR_PHONE

async def handle_phone(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    phone_input = update.message.text.strip()
    temp_pid = context.user_data.get("temp_patient_id")

    if not temp_pid:
        await update.message.reply_text("Session expired. Please send /start to begin.")
        return ConversationHandler.END

    logger.info(f"Patient verification attempted for ID '{temp_pid}'")
    patient = await verify_patient(temp_pid, phone_input)

    if not patient:
        logger.warning(f"Verification failed for Patient ID '{temp_pid}'")
        kb = get_verification_failed_keyboard()
        fail_text = (
            "❌ Patient verification failed.\n\n"
            "The Patient ID and phone number do not match our records.\n\n"
            "Please check the details and try again."
        )
        await update.message.reply_text(fail_text, reply_markup=kb)
        return ConversationHandler.END

    patient_id = patient["patientId"]
    patient_name = patient.get("patientName", "Patient")

    context.user_data["patient_id"] = patient_id
    context.user_data["patient_name"] = patient_name
    context.user_data["verified_at"] = datetime.utcnow().timestamp()
    context.user_data.pop("temp_patient_id", None)

    success_msg = (
        f"✅ Patient Verified\n\n"
        f"Patient ID: {patient_id}\n"
        f"Name: {patient_name}\n\n"
        f"Fetching your reports..."
    )
    await update.message.reply_text(success_msg)

    reports = await get_patient_reports(patient_id)
    if not reports:
        await update.message.reply_text("No reports are currently available for this patient.")
    else:
        kb = get_reports_list_keyboard(reports)
        await update.message.reply_text("Available Reports", reply_markup=kb)

    return ConversationHandler.END

async def cancel_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data.clear()
    await update.message.reply_text("Session ended securely. Use /start to access reports again.")
    return ConversationHandler.END

async def callback_query_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = query.data
    logger.info(f"Callback query received: '{data}'")

    if data == "action_cancel" or data == "action_exit":
        context.user_data.clear()
        await query.message.reply_text("Session ended securely. Use /start to access reports again.")
        return

    if data == "action_try_again":
        context.user_data.clear()
        welcome_text = (
            "Welcome to the AI Diagnosis Report Bot.\n\n"
            "To access your medical imaging report, please verify your details.\n\n"
            "Please enter your Patient ID."
        )
        await query.message.reply_text(welcome_text)
        return

    verified_pid = check_and_get_verified_patient_id(context)
    if not verified_pid:
        await query.message.reply_text("Session expired. Please use /start to verify again.")
        return

    if data == "action_back_to_reports":
        reports = await get_patient_reports(verified_pid)
        if not reports:
            await query.message.reply_text("No reports are currently available for this patient.")
        else:
            kb = get_reports_list_keyboard(reports)
            await query.message.reply_text("Available Reports", reply_markup=kb)
        return

    if data.startswith("report_select:"):
        report_id = data.split(":", 1)[1]
        logger.info(f"Report selected: '{report_id}' for patient '{verified_pid}'")
        
        details = await get_report_details(report_id, verified_pid)
        if not details:
            await query.message.reply_text("Patient verification failed or report not found.")
            return

        summary_text = (
            f"📄 Radiology Report\n\n"
            f"Report ID: {details['reportId']}\n"
            f"Patient ID: {details['patientId']}\n"
            f"Scan Type: {details['scanType']}\n"
            f"Created: {details['createdDate']}\n"
            f"Review Status: {details['reviewStatus']}\n"
            f"Possible Finding: {details['possibleFinding']}\n"
            f"Model Confidence: {details['confidencePct']}\n\n"
            f"⚠️ AI-assisted clinical decision support only. Final interpretation must be performed by a qualified healthcare professional."
        )
        kb = get_report_action_keyboard(details["reportId"])
        await query.message.reply_text(summary_text, reply_markup=kb)
        return

    if data.startswith("pdf_download:"):
        report_id = data.split(":", 1)[1]
        logger.info(f"PDF requested for report '{report_id}' by patient '{verified_pid}'")
        
        pdf_path = await get_report_pdf_path(report_id, verified_pid)
        if pdf_path and os.path.exists(pdf_path):
            filename = os.path.basename(pdf_path)
            await query.message.reply_text("Sending PDF report document...")
            with open(pdf_path, "rb") as pdf_file:
                await context.bot.send_document(
                    chat_id=update.effective_chat.id,
                    document=pdf_file,
                    filename=filename,
                    caption=f"📄 Radiology Report ({report_id})"
                )
            logger.info(f"PDF '{filename}' sent successfully.")
        else:
            logger.error(f"PDF missing or generation failed for report '{report_id}'")
            await query.message.reply_text("Report PDF is currently unavailable. Please contact the system administrator.")
        return
