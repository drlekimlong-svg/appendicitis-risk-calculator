import base64
import html
import json
import math
import re
import uuid
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from urllib.parse import urlencode

import numpy as np
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components
from sqlalchemy import text as sql_text

from models_config import APP_METADATA, INPUT_DEFS, MODELS, SECTION_ORDER, TERM_RULES


ROOT = Path(__file__).resolve().parent
ASSETS_DIR = ROOT / "assets"


st.set_page_config(
    page_title="Complicated Appendicitis Risk Calculator",
    page_icon="🩺",
    layout="wide",
)


TEXT = {
    "en": {
        "model_selection": "Model selection",
        "choose_model": "Choose one model",
        "research_warning": "Research / educational use only. Do not use this web app as a stand-alone basis for diagnosis or treatment.",
        "app_title": "Complicated Appendicitis Risk Calculator",
        "app_subtitle": "Risk estimation using three author-supplied multivariable models.",
        "input_form": "Input form",
        "input_form_caption": "Only the variables required by the selected model are shown.",
        "calculate_risk": "Calculate risk",
        "risk_calculated": "Risk calculated successfully.",
        "prediction": "Prediction",
        "enter_values_prompt": "Enter the variables in the form and click **Calculate risk**.",
        "predicted_probability": "Predicted probability of complicated appendicitis",
        "ci_label": "95% CI",
        "ci_note": "This interval is computed from the model's variance-covariance matrix on the logit scale and then transformed back to probability.",
        "ci_not_available": "95% CI is not shown because no variance-covariance matrix was provided for this model.",
        "linear_predictor": "Linear predictor (LP)",
        "crp_transformed": "CRP transformed for the model",
        "show_contributions": "Show term-by-term contributions",
        "show_coefficients": "Show coefficient table",
        "show_formula": "Show formula",
        "model_summary": "Model summary",
        "workbook_notes": "Model notes",
        "required_inputs": "Inputs required by this model",
        "quick_definitions": "Quick variable definitions",
        "quick_definitions_caption": "Hover over the ? icon next to each input to see the short definition. Use the compact reference below when needed.",
        "yes": "Yes",
        "no": "No",
        "print_report": "Print",
        "printable_report": "Printable report",
        "printable_report_caption": "Use the print button below to create a paper or PDF summary of the submitted variables and prediction result.",
        "report_title": "Prediction summary",
        "report_datetime": "Generated at",
        "report_model": "Model",
        "report_inputs": "Submitted variables",
        "report_results": "Prediction results",
        "report_parameter": "Parameter",
        "report_value": "Value",
        "report_footer": "For research and educational use. This calculator does not replace clinical judgment, imaging review, pathology, or institutional treatment protocols.",
        "warning_negative": "cannot be negative.",
        "coefficient_term": "Term",
        "coefficient_beta": "Beta",
        "coefficient_coding": "Coding / reference",
        "coefficient_or": "OR = exp(beta)",
        "notes_interactions": "Interactions",
        "notes_missing": "Missing data handling",
        "notes_note": "Note",
        "notes_splines": "Splines",
        "notes_vcov": "vcov",
        "report_probability": "Predicted probability",
        "report_lp": "Linear predictor (LP)",
        "report_crp_transformed": "CRP transformed for the model",
        "affiliation_heading": "Authors",
        "switch_to_english": "English",
        "switch_to_vietnamese": "Tiếng Việt",
        "version_label": "Version",
        "contact_label": "Contact",
        "guide_title": "Suggested workflow",
        "guide_point_1": "For the quickest practical estimate, start with Model 2 because it uses fewer inputs.",
        "guide_point_2": "When fuller clinical and CT information is available and you want a more detailed assessment, switch to Model 1 or Model 3.",
        "report_version": "Version",
        "report_contact": "Contact",
        "member_guest_status": "Guest mode",
        "member_logged_in_status": "Member signed in",
        "member_login": "Member login",
        "member_logout": "Log out",
        "member_login_not_configured": "Member login is not configured yet. The app is running in guest mode.",
        "member_guest_message": "Guest users can calculate and print results, but cannot save data.",
        "member_logged_in_as": "Signed in as",
        "member_member_can_save": "Signed-in members can save non-identifiable inputs and prediction results.",
        "member_not_authorized": "Your account is signed in but is not authorized for saving.",
        "member_db_not_configured": "Database storage is not configured, so saving is disabled.",
        "member_email_missing": "Signed in, but no email claim was returned by the identity provider.",
        "save_section_title": "Member data storage",
        "save_button": "Save current result",
        "save_success": "Result saved successfully.",
        "save_failure": "Could not save the result. Please check the database configuration.",
        "save_privacy_note": "Do not enter direct patient identifiers in this web app if you plan to save records.",
        "research_id_label": "Research ID (8 digits)",
        "research_id_help": "Use the study ID only. Enter exactly 8 digits; do not use medical record number, name, or phone number.",
        "research_id_placeholder": "Example: 24000001",
        "research_id_required": "Enter the 8-digit Research ID before saving.",
        "research_id_invalid": "Research ID must contain exactly 8 digits.",
        "save_requires_result": "Calculate a prediction first, then save.",
    },
    "vi": {
        "model_selection": "Lựa chọn mô hình",
        "choose_model": "Chọn mô hình",
        "research_warning": "Chỉ dùng cho nghiên cứu / giáo dục. Không sử dụng webapp này như căn cứ độc lập cho chẩn đoán hoặc điều trị.",
        "app_title": "Công cụ tính nguy cơ viêm ruột thừa có biến chứng",
        "app_subtitle": "Ước tính nguy cơ bằng ba mô hình đa biến do nhóm tác giả cung cấp.",
        "input_form": "Biểu mẫu nhập liệu",
        "input_form_caption": "Chỉ hiển thị các biến cần thiết cho mô hình đang chọn.",
        "calculate_risk": "Tính nguy cơ",
        "risk_calculated": "Đã tính nguy cơ thành công.",
        "prediction": "Kết quả dự đoán",
        "enter_values_prompt": "Nhập các biến trong biểu mẫu rồi bấm **Tính nguy cơ**.",
        "predicted_probability": "Xác suất dự đoán viêm ruột thừa có biến chứng",
        "ci_label": "KTC 95%",
        "ci_note": "Khoảng tin cậy này được tính từ ma trận hiệp phương sai-phương sai của mô hình trên thang logit, sau đó chuyển ngược về xác suất.",
        "ci_not_available": "Không hiển thị KTC 95% vì mô hình này không có ma trận hiệp phương sai-phương sai (vcov).",
        "linear_predictor": "Bộ dự báo tuyến tính (LP)",
        "crp_transformed": "CRP đã biến đổi cho mô hình",
        "show_contributions": "Xem đóng góp của từng hạng tử",
        "show_coefficients": "Xem bảng hệ số",
        "show_formula": "Xem công thức",
        "model_summary": "Tóm tắt mô hình",
        "workbook_notes": "Ghi chú mô hình",
        "required_inputs": "Các biến cần nhập cho mô hình này",
        "quick_definitions": "Định nghĩa ngắn các biến",
        "quick_definitions_caption": "Di chuột vào biểu tượng ? cạnh từng ô nhập để xem định nghĩa ngắn. Dùng bảng tham chiếu gọn bên dưới khi cần.",
        "yes": "Có",
        "no": "Không",
        "print_report": "In",
        "printable_report": "Bản in tổng hợp",
        "printable_report_caption": "Nhấn nút in bên dưới để tạo bản in giấy hoặc PDF gồm các biến đã nhập và kết quả dự đoán.",
        "report_title": "Tóm tắt kết quả dự đoán",
        "report_datetime": "Thời điểm tạo",
        "report_model": "Mô hình",
        "report_inputs": "Các biến đã nhập",
        "report_results": "Kết quả dự đoán",
        "report_parameter": "Thông số",
        "report_value": "Giá trị",
        "report_footer": "Chỉ dùng cho nghiên cứu và giáo dục. Công cụ này không thay thế đánh giá lâm sàng, đọc hình ảnh, giải phẫu bệnh hoặc phác đồ điều trị của cơ sở.",
        "warning_negative": "không được âm.",
        "coefficient_term": "Hạng tử",
        "coefficient_beta": "Hệ số beta",
        "coefficient_coding": "Mã hóa / mốc tham chiếu",
        "coefficient_or": "OR = exp(beta)",
        "notes_interactions": "Tương tác",
        "notes_missing": "Xử lý dữ liệu thiếu",
        "notes_note": "Ghi chú",
        "notes_splines": "Splines",
        "notes_vcov": "vcov",
        "report_probability": "Xác suất dự đoán",
        "report_lp": "Bộ dự báo tuyến tính (LP)",
        "report_crp_transformed": "CRP đã biến đổi cho mô hình",
        "affiliation_heading": "Tác giả",
        "switch_to_english": "English",
        "switch_to_vietnamese": "Tiếng Việt",
        "version_label": "Phiên bản",
        "contact_label": "Liên hệ",
        "guide_title": "Gợi ý cách sử dụng",
        "guide_point_1": "Nếu cần đánh giá nhanh gọn, nên bắt đầu với Mô hình 2 vì cần ít biến hơn.",
        "guide_point_2": "Khi có đầy đủ dữ liệu lâm sàng và CT và muốn đánh giá chi tiết hơn, chuyển sang Mô hình 1 hoặc Mô hình 3.",
        "report_version": "Phiên bản",
        "report_contact": "Liên hệ",
        "member_guest_status": "Chế độ khách",
        "member_logged_in_status": "Đã đăng nhập thành viên",
        "member_login": "Đăng nhập thành viên",
        "member_logout": "Đăng xuất",
        "member_login_not_configured": "Chưa cấu hình đăng nhập thành viên. Ứng dụng đang chạy ở chế độ khách.",
        "member_guest_message": "Khách vẫn có thể tính và in kết quả, nhưng không thể lưu dữ liệu.",
        "member_logged_in_as": "Đăng nhập với",
        "member_member_can_save": "Thành viên đã đăng nhập có thể lưu bộ biến đầu vào và kết quả dự đoán không định danh.",
        "member_not_authorized": "Tài khoản đã đăng nhập nhưng chưa được cấp quyền lưu dữ liệu.",
        "member_db_not_configured": "Chưa cấu hình nơi lưu dữ liệu nên chức năng lưu đang bị tắt.",
        "member_email_missing": "Đã đăng nhập nhưng nhà cung cấp định danh không trả về email.",
        "save_section_title": "Lưu dữ liệu thành viên",
        "save_button": "Lưu kết quả hiện tại",
        "save_success": "Đã lưu kết quả thành công.",
        "save_failure": "Không thể lưu kết quả. Vui lòng kiểm tra cấu hình cơ sở dữ liệu.",
        "save_privacy_note": "Không nhập thông tin định danh trực tiếp của người bệnh nếu anh dự định lưu bản ghi.",
        "research_id_label": "ID nghiên cứu (8 chữ số)",
        "research_id_help": "Chỉ dùng mã nghiên cứu. Nhập đúng 8 chữ số; không dùng số hồ sơ, họ tên hoặc số điện thoại.",
        "research_id_placeholder": "Ví dụ: 24000001",
        "research_id_required": "Hãy nhập ID nghiên cứu 8 chữ số trước khi lưu.",
        "research_id_invalid": "ID nghiên cứu phải gồm đúng 8 chữ số.",
        "save_requires_result": "Hãy tính nguy cơ trước rồi mới lưu.",
    },
}


SECTION_LABELS = {
    "Patient characteristics": {"en": "Patient characteristics", "vi": "Đặc điểm người bệnh"},
    "Clinical findings": {"en": "Clinical findings", "vi": "Dấu hiệu lâm sàng"},
    "Laboratory findings": {"en": "Laboratory findings", "vi": "Xét nghiệm"},
    "CT findings": {"en": "CT findings", "vi": "Hình ảnh CT"},
}


INPUT_LABELS = {
    "clin_anorexia": {"en": "Anorexia", "vi": "Chán ăn"},
    "clin_guarding_rebound_status": {"en": "Guarding / rebound status", "vi": "Đề kháng thành bụng / phản ứng dội"},
    "clin_heart_rate": {"en": "Heart rate (beats/min)", "vi": "Nhịp tim (lần/phút)"},
    "clin_nausea": {"en": "Nausea", "vi": "Buồn nôn"},
    "clin_pain_duration_hours": {"en": "Pain duration before admission (hours)", "vi": "Thời gian đau trước nhập viện (giờ)"},
    "ct_appendix_max_diameter_mm": {"en": "Maximum appendiceal diameter (mm)", "vi": "Đường kính lớn nhất ruột thừa (mm)"},
    "ct_appendix_wall_thickening": {"en": "Appendiceal wall thickening", "vi": "Dày thành ruột thừa"},
    "ct_fat_stranding_grade": {"en": "Periappendiceal fat stranding grade", "vi": "Mức độ thâm nhiễm mỡ quanh ruột thừa"},
    "ct_fecalith_present": {"en": "Fecalith present", "vi": "Có sỏi phân"},
    "ct_ileus_or_sbo": {"en": "Ileus or small-bowel obstruction", "vi": "Liệt ruột hoặc tắc ruột non"},
    "ct_luminal_fluid": {"en": "Luminal fluid", "vi": "Dịch trong lòng ruột thừa"},
    "ct_periappendiceal_free_fluid": {"en": "Periappendiceal free fluid", "vi": "Dịch tự do quanh ruột thừa"},
    "ct_wall_non_enhancement": {"en": "Wall non-enhancement", "vi": "Thành ruột thừa không ngấm thuốc"},
    "demo_age_years": {"en": "Age (years)", "vi": "Tuổi (năm)"},
    "lab_crp": {"en": "CRP (mg/L)", "vi": "CRP (mg/L)"},
    "lab_lymphocyte_abs": {"en": "Absolute lymphocyte count (×10⁹/L)", "vi": "Số lượng lympho tuyệt đối (×10⁹/L)"},
    "lab_wbc": {"en": "White blood cell count (×10⁹/L)", "vi": "Bạch cầu (×10⁹/L)"},
}


INPUT_HELP = {
    "clin_anorexia": {
        "en": "Self-reported loss of appetite at presentation.",
        "vi": "Người bệnh tự khai chán ăn tại thời điểm thăm khám ban đầu.",
    },
    "clin_guarding_rebound_status": {
        "en": "Choose: None; Guarding = involuntary abdominal wall tension on palpation; Rebound positive = pain increases with sudden release of pressure.",
        "vi": "Chọn: Không; Đề kháng = co cứng thành bụng không chủ ý khi sờ nắn; Phản ứng dội dương tính = đau tăng khi nhả tay đột ngột.",
    },
    "clin_heart_rate": {
        "en": "Initial heart rate at presentation, in beats per minute.",
        "vi": "Nhịp tim ban đầu khi nhập viện, tính bằng lần/phút.",
    },
    "clin_nausea": {
        "en": "Self-reported nausea at presentation.",
        "vi": "Người bệnh tự khai buồn nôn tại thời điểm thăm khám ban đầu.",
    },
    "clin_pain_duration_hours": {
        "en": "Time from onset of abdominal pain to hospital admission, in hours.",
        "vi": "Thời gian từ khi khởi phát đau bụng đến khi nhập viện, tính bằng giờ.",
    },
    "ct_appendix_max_diameter_mm": {
        "en": "Maximum outer-to-outer appendiceal diameter. Prefer an intact segment, measured perpendicular to the appendix axis; MPR is preferred when available.",
        "vi": "Đường kính ngoài-ngoài lớn nhất của ruột thừa. Ưu tiên đo trên đoạn còn nguyên vẹn, vuông góc với trục ruột thừa; ưu tiên MPR khi có thể.",
    },
    "ct_appendix_wall_thickening": {
        "en": "Appendiceal wall thickening, typically wall thickness ≥ 3 mm on a clearly visualized segment.",
        "vi": "Dày thành ruột thừa, thường gợi ý khi bề dày thành ≥ 3 mm trên đoạn nhìn rõ.",
    },
    "ct_fat_stranding_grade": {
        "en": "Grade periappendiceal fat stranding as None, Mild, Moderate, or Severe. Severe means extension beyond the mesoappendix or stranding disproportionate to wall thickening.",
        "vi": "Chấm mức độ thâm nhiễm mỡ quanh ruột thừa là Không, Ít, Trung bình hoặc Nhiều. Mức Nhiều là lan ra ngoài mạc treo ruột thừa hoặc thâm nhiễm không tương xứng với dày thành.",
    },
    "ct_fecalith_present": {
        "en": "Appendicolith/fecalith: a well-defined round or oval calcified or high-attenuation focus within the appendix; it may be extraluminal if perforation has occurred.",
        "vi": "Sỏi phân ruột thừa: cấu trúc tròn hoặc bầu dục, giới hạn rõ, tăng đậm độ hoặc vôi hóa nằm trong lòng ruột thừa; có thể nằm ngoài lòng nếu đã vỡ.",
    },
    "ct_ileus_or_sbo": {
        "en": "Ileus = bowel dilatation without a clear transition point. SBO = small-bowel dilatation, usually > 2.5 cm, with a transition point.",
        "vi": "Liệt ruột = giãn ruột nhưng không có điểm chuyển tiếp rõ. Tắc ruột non = giãn ruột non, thường > 2,5 cm, kèm điểm chuyển tiếp.",
    },
    "ct_luminal_fluid": {
        "en": "Fluid attenuation within the appendiceal lumen rather than gas or a fecalith.",
        "vi": "Dịch nằm trong lòng ruột thừa, không phải khí hay sỏi phân.",
    },
    "ct_periappendiceal_free_fluid": {
        "en": "Unencapsulated low-attenuation free fluid around the appendix or in the right iliac fossa; distinguish from fat stranding.",
        "vi": "Dịch tự do ngoài lòng, không có vỏ bao, quanh ruột thừa hoặc vùng hố chậu phải; cần phân biệt với thâm nhiễm mỡ.",
    },
    "ct_wall_non_enhancement": {
        "en": "Focal mural non-enhancement or wall discontinuity on contrast-enhanced CT, suggesting ischemia, necrosis, or perforation.",
        "vi": "Khuyết thuốc hoặc mất liên tục thành trên CT có tiêm cản quang, gợi ý thiếu máu, hoại tử hoặc thủng.",
    },
    "demo_age_years": {
        "en": "Age in completed years. Adult patients only.",
        "vi": "Tuổi tính theo năm tròn. Chỉ áp dụng cho người lớn.",
    },
    "lab_crp": {
        "en": "Initial serum CRP in mg/L. Internally transformed as log(1 + CRP) when required by the model.",
        "vi": "CRP huyết thanh ban đầu, đơn vị mg/L. Sẽ được biến đổi nội bộ thành log(1 + CRP) khi mô hình yêu cầu.",
    },
    "lab_lymphocyte_abs": {
        "en": "Absolute lymphocyte count from the initial complete blood count, in ×10⁹/L.",
        "vi": "Số lượng lympho tuyệt đối từ công thức máu ban đầu, đơn vị ×10⁹/L.",
    },
    "lab_wbc": {
        "en": "White blood cell count from the initial complete blood count, in ×10⁹/L.",
        "vi": "Số lượng bạch cầu từ công thức máu ban đầu, đơn vị ×10⁹/L.",
    },
}


VALUE_LABELS = {
    "clin_guarding_rebound_status": {
        "none": {"en": "None", "vi": "Không"},
        "guarding": {"en": "Guarding", "vi": "Đề kháng"},
        "rebound_positive": {"en": "Rebound tenderness positive", "vi": "Phản ứng dội dương tính"},
    },
    "ct_fat_stranding_grade": {
        "Không": {"en": "None", "vi": "Không"},
        "Ít": {"en": "Mild", "vi": "Ít"},
        "Trung Bình": {"en": "Moderate", "vi": "Trung bình"},
        "Nhiều": {"en": "Severe", "vi": "Nhiều"},
    },
}


MODEL_TRANSLATIONS = {
    "model1_primary_lasso": {
        "short_en": "Model 1 — Primary LASSO",
        "short_vi": "Mô hình 1 — LASSO đầy đủ",
        "display_en": "Model 1 — Primary full penalized logistic LASSO",
        "display_vi": "Mô hình 1 — Hồi quy logistic LASSO phạt đầy đủ",
        "title_en": "Model 1. Primary full penalized logistic LASSO (lambda.1se)",
        "title_vi": "Mô hình 1. Hồi quy logistic LASSO phạt đầy đủ (lambda.1se)",
    },
    "model2_parsimonious": {
        "short_en": "Model 2 — Parsimonious LASSO",
        "short_vi": "Mô hình 2 — LASSO tinh gọn",
        "display_en": "Model 2 — Parsimonious constrained logistic LASSO",
        "display_vi": "Mô hình 2 — Hồi quy logistic LASSO ràng buộc tinh gọn",
        "title_en": "Model 2. Parsimonious constrained logistic LASSO (lambda_5_1se)",
        "title_vi": "Mô hình 2. Hồi quy logistic LASSO ràng buộc tinh gọn (lambda_5_1se)",
    },
    "model3_stepwise": {
        "short_en": "Model 3 — Stepwise logistic regression",
        "short_vi": "Mô hình 3 — Hồi quy logistic từng bước",
        "display_en": "Model 3 — Backward stepwise logistic regression (AIC)",
        "display_vi": "Mô hình 3 — Hồi quy logistic loại biến lùi từng bước (AIC)",
        "title_en": "Model 3. Backward stepwise logistic regression (AIC)",
        "title_vi": "Mô hình 3. Hồi quy logistic loại biến lùi từng bước (AIC)",
    },
}


NOTE_LABELS = {
    "Interactions": {"en": "Interactions", "vi": "Tương tác"},
    "Missing data handling": {"en": "Missing data handling", "vi": "Xử lý dữ liệu thiếu"},
    "Note": {"en": "Note", "vi": "Ghi chú"},
    "Splines": {"en": "Splines", "vi": "Splines"},
    "vcov": {"en": "vcov", "vi": "vcov"},
}


def t(lang: str, key: str) -> str:
    return TEXT[lang][key]


AUTHORS_BY_LANG = {
    "en": APP_METADATA.get(
        "author_names_en",
        APP_METADATA.get(
            "author_names",
            [name.strip() for name in APP_METADATA.get("author_name", "").split(";") if name.strip()],
        ),
    ),
    "vi": APP_METADATA.get(
        "author_names_vi",
        APP_METADATA.get(
            "author_names",
            [name.strip() for name in APP_METADATA.get("author_name", "").split(";") if name.strip()],
        ),
    ),
}

AFFILIATIONS = {
    "en": APP_METADATA.get(
        "affiliation_lines_en",
        APP_METADATA.get(
            "affiliation_lines",
            [
                "Department of Surgery, Faculty of Medicine, Pham Ngoc Thach University of Medicine",
                "Nhan Dan Gia Dinh Hospital",
            ],
        ),
    ),
    "vi": APP_METADATA.get(
        "affiliation_lines_vi",
        [
            "Bộ môn Ngoại khoa - Khoa Y - Trường Đại học Y khoa Phạm Ngọc Thạch",
            "Bệnh viện Nhân dân Gia Định",
        ],
    ),
}

FOOTER_NOTES = {
    "en": APP_METADATA.get(
        "footer_note_en",
        APP_METADATA.get(
            "footer_note",
            "For research and educational use. This calculator does not replace clinical judgment, imaging review, pathology, or institutional treatment protocols.",
        ),
    ),
    "vi": APP_METADATA.get(
        "footer_note_vi",
        "Chỉ dùng cho nghiên cứu và giáo dục. Công cụ này không thay thế đánh giá lâm sàng, đọc hình ảnh, giải phẫu bệnh hoặc phác đồ điều trị của cơ sở.",
    ),
}

CONTACT_EMAIL = APP_METADATA.get("contact_email", "Longlk@pnt.edu.vn")
APP_VERSION = str(APP_METADATA.get("version", "1.2.1"))


def get_query_param(name: str) -> str | None:
    try:
        value = st.query_params.get(name)
    except Exception:
        try:
            value = st.experimental_get_query_params().get(name)
        except Exception:
            value = None

    if isinstance(value, list):
        return str(value[0]) if value else None
    if value is None:
        return None
    return str(value)


def sync_query_params(model_key: str, lang: str) -> None:
    current_model = get_query_param("model")
    current_lang = get_query_param("lang")
    if current_model == model_key and current_lang == lang:
        return

    try:
        st.query_params["model"] = model_key
        st.query_params["lang"] = lang
    except Exception:
        try:
            st.experimental_set_query_params(model=model_key, lang=lang)
        except Exception:
            pass


def guide_model_link(model_key: str, lang: str) -> str:
    labels = {
        "model1_primary_lasso": {"en": "Model 1", "vi": "Mô hình 1"},
        "model2_parsimonious": {"en": "Model 2", "vi": "Mô hình 2"},
        "model3_stepwise": {"en": "Model 3", "vi": "Mô hình 3"},
    }
    label = labels[model_key][lang]
    href = "?" + urlencode({"model": model_key, "lang": lang})
    return (
        f'<a href="{href}" style="color:inherit; text-decoration:underline; '
        f'font-weight:600;">{html.escape(label)}</a>'
    )


def guide_point_html(point_number: int, lang: str) -> str:
    if point_number == 1:
        if lang == "vi":
            return (
                f'Nếu cần đánh giá nhanh gọn, nên bắt đầu với '
                f'{guide_model_link("model2_parsimonious", lang)} vì cần ít biến hơn.'
            )
        return (
            f'For the quickest practical estimate, start with '
            f'{guide_model_link("model2_parsimonious", lang)} because it uses fewer inputs.'
        )

    if lang == "vi":
        return (
            f'Khi có đầy đủ dữ liệu lâm sàng và CT và muốn đánh giá chi tiết hơn, '
            f'chuyển sang {guide_model_link("model1_primary_lasso", lang)} hoặc '
            f'{guide_model_link("model3_stepwise", lang)}.'
        )
    return (
        f'When fuller clinical and CT information is available and you want a more detailed assessment, '
        f'switch to {guide_model_link("model1_primary_lasso", lang)} or '
        f'{guide_model_link("model3_stepwise", lang)}.'
    )


def user_info_dict() -> dict:
    try:
        return st.user.to_dict()
    except Exception:
        try:
            return dict(st.user)
        except Exception:
            return {}


def auth_configured() -> bool:
    try:
        auth_section = st.secrets.get("auth", {})
    except Exception:
        return False

    required_keys = ["redirect_uri", "cookie_secret", "client_id", "client_secret", "server_metadata_url"]
    return all(bool(auth_section.get(key)) for key in required_keys)


def user_is_logged_in() -> bool:
    try:
        return bool(getattr(st.user, "is_logged_in", False))
    except Exception:
        return False


def current_user_email() -> str:
    info = user_info_dict()
    for key in ("email", "preferred_username", "upn", "login_hint"):
        value = info.get(key)
        if value:
            return str(value)
    return ""


def current_user_name() -> str:
    info = user_info_dict()
    for key in ("name", "given_name", "preferred_username"):
        value = info.get(key)
        if value:
            return str(value)
    return ""


def allowed_member_emails() -> set[str]:
    try:
        members_section = st.secrets.get("members", {})
    except Exception:
        return set()

    raw_values = members_section.get("allowed_emails", [])
    return {str(item).strip().lower() for item in raw_values if str(item).strip()}


def normalize_research_id(raw_value: str) -> str:
    return str(raw_value or "").strip()


def research_id_is_valid(raw_value: str) -> bool:
    return bool(re.fullmatch(r"\d{8}", normalize_research_id(raw_value)))


def member_can_save() -> tuple[bool, str]:
    if not auth_configured():
        return False, "auth_not_configured"

    if not user_is_logged_in():
        return False, "guest"

    allowed = allowed_member_emails()
    email = current_user_email().strip().lower()

    if allowed:
        if not email:
            return False, "email_missing"
        if email not in allowed:
            return False, "not_authorized"

    return True, "ok"


@st.cache_resource(show_spinner=False)
def get_db_engine():
    try:
        conn = st.connection("app_db", type="sql")
        return conn.engine
    except Exception:
        return None


@st.cache_resource(show_spinner=False)
def initialize_storage() -> bool:
    engine = get_db_engine()
    if engine is None:
        return False

    create_stmt = sql_text(
        """
        CREATE TABLE IF NOT EXISTS saved_predictions (
            id TEXT PRIMARY KEY,
            created_at_utc TEXT NOT NULL,
            user_email TEXT,
            user_name TEXT,
            research_id TEXT,
            model_key TEXT NOT NULL,
            model_display_name TEXT NOT NULL,
            ui_language TEXT NOT NULL,
            app_version TEXT NOT NULL,
            probability REAL NOT NULL,
            ci_low REAL,
            ci_high REAL,
            linear_predictor REAL NOT NULL,
            input_json TEXT NOT NULL,
            result_json TEXT NOT NULL
        )
        """
    )

    alter_stmt = sql_text("ALTER TABLE saved_predictions ADD COLUMN IF NOT EXISTS research_id TEXT")

    try:
        with engine.begin() as conn:
            conn.execute(create_stmt)
            conn.execute(alter_stmt)
        return True
    except Exception:
        return False


def database_ready() -> bool:
    return bool(initialize_storage())


def save_result_record(model_key: str, lang: str, research_id: str) -> tuple[bool, str]:
    engine = get_db_engine()
    if engine is None or not initialize_storage():
        return False, "db_not_configured"

    result = st.session_state.get(f"result_{model_key}")
    values = st.session_state.get(f"inputs_{model_key}")
    if not result or not values:
        return False, "no_result"

    record_id = str(uuid.uuid4())
    created_at_utc = datetime.utcnow().replace(microsecond=0).isoformat() + "Z"
    probability = float(result["probability"])
    ci_low = float(result["ci"]["prob_low"]) if result.get("ci") is not None else None
    ci_high = float(result["ci"]["prob_high"]) if result.get("ci") is not None else None
    lp = float(result["lp"])
    transformed_crp = result.get("transformed_crp")

    payload_inputs = {name: values[name] for name in model_required_inputs(model_key)}
    payload_results = {
        "probability": probability,
        "ci_low": ci_low,
        "ci_high": ci_high,
        "linear_predictor": lp,
        "transformed_crp": float(transformed_crp) if transformed_crp is not None else None,
    }

    insert_stmt = sql_text(
        """
        INSERT INTO saved_predictions (
            id, created_at_utc, user_email, user_name, research_id, model_key, model_display_name,
            ui_language, app_version, probability, ci_low, ci_high, linear_predictor,
            input_json, result_json
        )
        VALUES (
            :id, :created_at_utc, :user_email, :user_name, :research_id, :model_key, :model_display_name,
            :ui_language, :app_version, :probability, :ci_low, :ci_high, :linear_predictor,
            :input_json, :result_json
        )
        """
    )

    params = {
        "id": record_id,
        "created_at_utc": created_at_utc,
        "user_email": current_user_email(),
        "user_name": current_user_name(),
        "research_id": normalize_research_id(research_id),
        "model_key": model_key,
        "model_display_name": model_display_name(model_key, lang),
        "ui_language": lang,
        "app_version": APP_VERSION,
        "probability": probability,
        "ci_low": ci_low,
        "ci_high": ci_high,
        "linear_predictor": lp,
        "input_json": json.dumps(payload_inputs, ensure_ascii=False),
        "result_json": json.dumps(payload_results, ensure_ascii=False),
    }

    try:
        with engine.begin() as conn:
            conn.execute(insert_stmt, params)
        return True, record_id
    except Exception:
        return False, "save_error"


def resolve_asset_path(filename: str) -> Path:
    candidates = [
        ASSETS_DIR / filename,
        ROOT / filename,
        Path.cwd() / "assets" / filename,
        Path.cwd() / filename,
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    return ASSETS_DIR / filename


LOGO_HOSPITAL_PATH = resolve_asset_path("logo_gia_dinh.png")
LOGO_UNIVERSITY_PATH = resolve_asset_path("logo_pnt.png")


def image_to_base64(path: Path) -> str:
    if not path.exists():
        return ""
    return base64.b64encode(path.read_bytes()).decode("utf-8")


LOGO_HOSPITAL_BASE64 = image_to_base64(LOGO_HOSPITAL_PATH)
LOGO_UNIVERSITY_BASE64 = image_to_base64(LOGO_UNIVERSITY_PATH)


def version_text(lang: str) -> str:
    return f"{t(lang, 'version_label')} {APP_VERSION}"


def contact_text(lang: str) -> str:
    return f"{t(lang, 'contact_label')}: {CONTACT_EMAIL}"


def sigmoid(x: float) -> float:
    if x >= 0:
        z = math.exp(-x)
        return 1.0 / (1.0 + z)
    z = math.exp(x)
    return z / (1.0 + z)


def evaluate_term(term: str, values: dict) -> float:
    rule = TERM_RULES[term]
    rule_type = rule["type"]
    input_name = rule["input"]

    if rule_type == "direct":
        return float(values[input_name])

    if rule_type == "bool":
        return 1.0 if bool(values[input_name]) else 0.0

    if rule_type == "equals":
        return 1.0 if values[input_name] == rule["value"] else 0.0

    if rule_type == "log1p":
        return math.log1p(float(values[input_name]))

    raise ValueError(f"Unsupported rule type for term {term}: {rule_type}")


def model_required_inputs(model_key: str) -> list[str]:
    model = MODELS[model_key]
    needed = []
    seen = set()

    for term in model["active_terms"]:
        rule = TERM_RULES[term]
        input_name = rule["input"]
        if input_name not in seen:
            seen.add(input_name)
            needed.append(input_name)

    return needed


def input_label(input_name: str, lang: str) -> str:
    return INPUT_LABELS.get(input_name, {}).get(lang, INPUT_DEFS[input_name].get("label", input_name))


def input_help(input_name: str, lang: str):
    return INPUT_HELP.get(input_name, {}).get(lang, INPUT_DEFS[input_name].get("help"))


def section_label(section: str, lang: str) -> str:
    return SECTION_LABELS.get(section, {}).get(lang, section)


def option_label(input_name: str, value, lang: str) -> str:
    if input_name in VALUE_LABELS and value in VALUE_LABELS[input_name]:
        return VALUE_LABELS[input_name][value][lang]
    return str(value)


def bool_label(value: bool, lang: str) -> str:
    return t(lang, "yes") if value else t(lang, "no")


def model_short_name(model_key: str, lang: str) -> str:
    key = "short_en" if lang == "en" else "short_vi"
    return MODEL_TRANSLATIONS.get(model_key, {}).get(key, MODELS[model_key]["short_name"])


def model_display_name(model_key: str, lang: str) -> str:
    key = "display_en" if lang == "en" else "display_vi"
    return MODEL_TRANSLATIONS.get(model_key, {}).get(key, MODELS[model_key]["display_name"])


def model_title(model_key: str, lang: str) -> str:
    key = "title_en" if lang == "en" else "title_vi"
    return MODEL_TRANSLATIONS.get(model_key, {}).get(key, MODELS[model_key]["title"])


def note_label(label: str, lang: str) -> str:
    return NOTE_LABELS.get(label, {}).get(lang, label)


def format_number(value: float, fmt: str) -> str:
    try:
        return fmt % float(value)
    except Exception:
        return str(value)


def format_value_for_display(input_name: str, value, lang: str) -> str:
    spec = INPUT_DEFS[input_name]

    if spec["type"] == "number":
        return format_number(float(value), spec["format"])

    if spec["type"] == "bool":
        return bool_label(bool(value), lang)

    if spec["type"] == "select":
        return option_label(input_name, value, lang)

    return str(value)


def validate_inputs(model_key: str, values: dict, lang: str) -> list[str]:
    warnings = []
    required = model_required_inputs(model_key)

    for name in required:
        value = values[name]
        if isinstance(value, (int, float)) and not isinstance(value, bool) and value < 0:
            warnings.append(f"{input_label(name, lang)} {t(lang, 'warning_negative')}")

    return warnings


def predict(model_key: str, values: dict) -> dict:
    model = MODELS[model_key]
    lp = float(model["intercept"])

    contributions = []
    for term in model["active_terms"]:
        x_value = evaluate_term(term, values)
        beta = float(model["coefficients"][term])
        contribution = beta * x_value
        coding = next((row["coding"] for row in model["rows"] if row["term"] == term), term)
        contributions.append(
            {
                "term": term,
                "display": coding,
                "x_value": x_value,
                "beta": beta,
                "contribution": contribution,
            }
        )
        lp += contribution

    probability = sigmoid(lp)

    ci = None
    if model.get("ci_supported"):
        ci_order = model["ci_order"]
        x_vector = np.array([1.0] + [evaluate_term(term, values) for term in ci_order[1:]], dtype=float)
        vcov = np.array(model["vcov"], dtype=float)
        var_lp = float(x_vector @ vcov @ x_vector.T)
        var_lp = max(var_lp, 0.0)
        se_lp = math.sqrt(var_lp)
        z = 1.96
        ci_lp_low = lp - z * se_lp
        ci_lp_high = lp + z * se_lp
        ci = {
            "lp_low": ci_lp_low,
            "lp_high": ci_lp_high,
            "prob_low": sigmoid(ci_lp_low),
            "prob_high": sigmoid(ci_lp_high),
            "se_lp": se_lp,
        }

    return {
        "lp": lp,
        "probability": probability,
        "ci": ci,
        "contributions": pd.DataFrame(contributions),
        "transformed_crp": math.log1p(float(values["lab_crp"])) if "lab_crp" in values else None,
    }


def render_widget(input_name: str, lang: str):
    spec = INPUT_DEFS[input_name]
    widget_key = f"widget_{input_name}"
    label = input_label(input_name, lang)
    help_text = input_help(input_name, lang)

    if spec["type"] == "number":
        return st.number_input(
            label,
            min_value=float(spec["min_value"]),
            max_value=float(spec["max_value"]),
            value=float(spec["default"]),
            step=float(spec["step"]),
            format=spec["format"],
            help=help_text,
            key=widget_key,
        )

    if spec["type"] == "bool":
        return st.selectbox(
            label,
            options=[False, True],
            index=1 if spec.get("default", False) else 0,
            format_func=lambda val: bool_label(val, lang),
            help=help_text,
            key=widget_key,
        )

    if spec["type"] == "select":
        option_values = [option["value"] for option in spec["options"]]
        default_value = spec["default"]
        default_index = option_values.index(default_value) if default_value in option_values else 0
        return st.selectbox(
            label,
            options=option_values,
            index=default_index,
            format_func=lambda val: option_label(input_name, val, lang),
            help=help_text,
            key=widget_key,
        )

    raise ValueError(f"Unsupported widget type: {spec['type']}")


def render_auth_controls(lang: str):
    if not auth_configured():
        st.info(t(lang, "member_guest_status"))
        st.caption(t(lang, "member_login_not_configured"))
        return

    if not user_is_logged_in():
        st.info(t(lang, "member_guest_status"))
        st.caption(t(lang, "member_guest_message"))
        if st.button(t(lang, "member_login"), key="member_login_button", use_container_width=True):
            st.login()
        return

    display_name = current_user_name() or current_user_email() or t(lang, "member_logged_in_status")
    st.success(t(lang, "member_logged_in_status"))
    st.caption(f"{t(lang, 'member_logged_in_as')}: {display_name}")
    email = current_user_email()
    if email and display_name != email:
        st.caption(email)
    if st.button(t(lang, "member_logout"), key="member_logout_button", use_container_width=True):
        st.logout()


def render_header(lang: str):
    left, center, right = st.columns([0.24, 0.56, 0.20], gap="small")

    hospital_logo_html = (
        f"<img src='data:image/png;base64,{LOGO_HOSPITAL_BASE64}' alt='Hospital logo' style='max-width:84px; max-height:84px; width:auto; height:auto; object-fit:contain;'>"
        if LOGO_HOSPITAL_BASE64
        else ""
    )
    university_logo_html = (
        f"<img src='data:image/png;base64,{LOGO_UNIVERSITY_BASE64}' alt='University logo' style='max-width:84px; max-height:84px; width:auto; height:auto; object-fit:contain;'>"
        if LOGO_UNIVERSITY_BASE64
        else ""
    )

    with left:
        logos = []
        if hospital_logo_html:
            logos.append(hospital_logo_html)
        if university_logo_html:
            logos.append(university_logo_html)
        if logos:
            st.markdown(
                f"<div style='display:flex; align-items:center; justify-content:flex-start; gap:14px; min-height:96px; padding-top:6px;'>"
                + "".join(logos)
                + "</div>",
                unsafe_allow_html=True,
            )

    with center:
        authors_text = ", ".join(AUTHORS_BY_LANG[lang])
        affiliation_lines = "<br>".join(html.escape(line) for line in AFFILIATIONS[lang])
        st.markdown(
            f"""
            <div style="text-align:center; padding-top:4px;">
                <h1 style="margin-bottom:0.15rem;">{html.escape(t(lang, 'app_title'))}</h1>
                <div style="font-size:1.05rem; margin-bottom:0.55rem;">{html.escape(t(lang, 'app_subtitle'))}</div>
                <div style="font-weight:600; margin-bottom:0.25rem; line-height:1.5;">{html.escape(t(lang, 'affiliation_heading'))}: {html.escape(authors_text)}</div>
                <div style="line-height:1.5;">{affiliation_lines}</div>
                <div style="margin-top:0.55rem; display:flex; justify-content:center; flex-wrap:wrap; gap:8px;">
                    <span style="display:inline-block; padding:0.35rem 0.75rem; background:rgba(148, 163, 184, 0.12); border:1px solid rgba(148, 163, 184, 0.32); border-radius:999px; font-size:0.92rem; color:inherit;">
                        {html.escape(version_text(lang))}
                    </span>
                    <span style="display:inline-block; padding:0.35rem 0.75rem; background:rgba(148, 163, 184, 0.12); border:1px solid rgba(148, 163, 184, 0.32); border-radius:999px; font-size:0.92rem; color:inherit;">
                        {html.escape(t(lang, 'contact_label'))}: <a href="mailto:{html.escape(CONTACT_EMAIL)}">{html.escape(CONTACT_EMAIL)}</a>
                    </span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with right:
        if st.button(
            t(lang, "switch_to_english") if lang == "vi" else t(lang, "switch_to_vietnamese"),
            key="toggle_language_button",
            use_container_width=True,
        ):
            st.session_state["lang"] = "en" if lang == "vi" else "vi"
            current_model = st.session_state.get("selected_model", list(MODELS.keys())[0])
            sync_query_params(model_key=current_model, lang=st.session_state["lang"])
            st.rerun()
        render_auth_controls(lang)


def render_guidance(lang: str):
    point_1 = guide_point_html(1, lang)
    point_2 = guide_point_html(2, lang)
    st.markdown(
        f"""
        <div style="border:1px solid rgba(148, 163, 184, 0.38); background:rgba(148, 163, 184, 0.10); padding:0.95rem 1rem; border-radius:12px; margin-bottom:0.75rem; color:inherit;">
            <div style="font-weight:700; margin-bottom:0.45rem; color:inherit;">{html.escape(t(lang, 'guide_title'))}</div>
            <ul style="margin:0.1rem 0 0 1.15rem; padding:0; line-height:1.65; color:inherit;">
                <li style="color:inherit;">{point_1}</li>
                <li style="color:inherit;">{point_2}</li>
            </ul>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_quick_definitions(model_key: str, lang: str):
    required_fields = model_required_inputs(model_key)
    section_to_inputs = defaultdict(list)
    for name in required_fields:
        section_to_inputs[INPUT_DEFS[name]["section"]].append(name)

    container = st.popover(t(lang, "quick_definitions")) if hasattr(st, "popover") else st.expander(t(lang, "quick_definitions"), expanded=False)
    with container:
        st.caption(t(lang, "quick_definitions_caption"))
        for section in SECTION_ORDER:
            names = section_to_inputs.get(section, [])
            if not names:
                continue
            st.markdown(f"**{section_label(section, lang)}**")
            for name in names:
                help_text = input_help(name, lang) or ""
                st.markdown(f"- **{input_label(name, lang)}**: {help_text}")

def show_model_summary(model_key: str, lang: str):
    model = MODELS[model_key]
    st.subheader(t(lang, "model_summary"))
    st.markdown(f"**{model_display_name(model_key, lang)}**")
    st.caption(model_title(model_key, lang))

    with st.expander(t(lang, "workbook_notes"), expanded=True):
        for label, value in model["notes"].items():
            st.write(f"- **{note_label(label, lang)}:** {value}")

    required_fields = model_required_inputs(model_key)
    section_to_inputs = defaultdict(list)
    for name in required_fields:
        section_to_inputs[INPUT_DEFS[name]["section"]].append(name)

    with st.expander(t(lang, "required_inputs"), expanded=True):
        for section in SECTION_ORDER:
            names = section_to_inputs.get(section, [])
            if not names:
                continue
            st.markdown(f"**{section_label(section, lang)}**")
            for name in names:
                st.write(f"- {input_label(name, lang)}")
        render_quick_definitions(model_key, lang)

    with st.expander(t(lang, "show_coefficients"), expanded=False):
        coef_df = pd.DataFrame(model["rows"]).rename(
            columns={
                "term": t(lang, "coefficient_term"),
                "beta": t(lang, "coefficient_beta"),
                "coding": t(lang, "coefficient_coding"),
                "or": t(lang, "coefficient_or"),
            }
        )
        st.dataframe(coef_df, use_container_width=True, hide_index=True)

    with st.expander(t(lang, "show_formula"), expanded=False):
        st.code(model["formula"])


def render_member_save_section(model_key: str, lang: str):
    st.markdown(f"### {t(lang, 'save_section_title')}")
    st.caption(t(lang, "save_privacy_note"))

    if not auth_configured():
        st.info(t(lang, "member_login_not_configured"))
        return

    if not user_is_logged_in():
        st.info(t(lang, "member_guest_message"))
        if st.button(t(lang, "member_login"), key=f"member_login_from_save_{model_key}", use_container_width=True):
            st.login()
        return

    email = current_user_email()
    name = current_user_name()
    signed_in_as = name or email or t(lang, "member_logged_in_status")
    st.caption(f"{t(lang, 'member_logged_in_as')}: {signed_in_as}")
    if email and signed_in_as != email:
        st.caption(email)

    can_save, status = member_can_save()
    if not can_save:
        if status == "not_authorized":
            st.warning(t(lang, "member_not_authorized"))
        elif status == "email_missing":
            st.warning(t(lang, "member_email_missing"))
        else:
            st.info(t(lang, "member_guest_message"))
        return

    if not database_ready():
        st.warning(t(lang, "member_db_not_configured"))
        return

    st.success(t(lang, "member_member_can_save"))

    research_id = st.text_input(
        t(lang, "research_id_label"),
        value=st.session_state.get(f"research_id_{model_key}", ""),
        max_chars=8,
        placeholder=t(lang, "research_id_placeholder"),
        help=t(lang, "research_id_help"),
        key=f"research_id_{model_key}",
    )
    research_id_clean = normalize_research_id(research_id)
    has_result = bool(st.session_state.get(f"result_{model_key}"))

    if not research_id_clean:
        st.info(t(lang, "research_id_required"))
    elif not research_id_is_valid(research_id_clean):
        st.warning(t(lang, "research_id_invalid"))

    if not has_result:
        st.info(t(lang, "save_requires_result"))

    if st.button(
        t(lang, "save_button"),
        key=f"save_button_{model_key}",
        use_container_width=True,
        disabled=(not research_id_is_valid(research_id_clean)) or (not has_result),
    ):
        ok, _ = save_result_record(model_key, lang, research_id_clean)
        if ok:
            st.success(t(lang, "save_success"))
        else:
            st.error(t(lang, "save_failure"))

def build_print_report_html(model_key: str, lang: str) -> str:
    result = st.session_state.get(f"result_{model_key}")
    values = st.session_state.get(f"inputs_{model_key}")
    if not result or not values:
        return ""

    required_inputs = model_required_inputs(model_key)
    input_rows = "".join(
        f"<tr><td>{html.escape(input_label(name, lang))}</td><td>{html.escape(format_value_for_display(name, values[name], lang))}</td></tr>"
        for name in required_inputs
    )

    probability_pct = result["probability"] * 100.0
    result_rows = [
        (t(lang, "report_probability"), f"{probability_pct:.1f}%"),
        (t(lang, "report_lp"), f"{result['lp']:.4f}"),
    ]

    if result["ci"] is not None:
        ci_low = result["ci"]["prob_low"] * 100.0
        ci_high = result["ci"]["prob_high"] * 100.0
        ci_text = f"{ci_low:.1f}% to {ci_high:.1f}%" if lang == "en" else f"{ci_low:.1f}% đến {ci_high:.1f}%"
        result_rows.insert(1, (t(lang, "ci_label"), ci_text))

    if "lab_crp_model" in MODELS[model_key]["active_terms"] and result["transformed_crp"] is not None:
        result_rows.append((t(lang, "report_crp_transformed"), f"{result['transformed_crp']:.4f}"))

    result_html = "".join(
        f"<tr><td>{html.escape(label)}</td><td>{html.escape(value)}</td></tr>" for label, value in result_rows
    )

    authors_text = ", ".join(AUTHORS_BY_LANG[lang])
    model_text = model_display_name(model_key, lang)
    now_text = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    affiliations_html = "<br>".join(html.escape(line) for line in AFFILIATIONS[lang])

    logo_hospital_html = (
        f"<img src='data:image/png;base64,{LOGO_HOSPITAL_BASE64}' alt='Hospital logo' style='max-width:72px; max-height:72px;'>"
        if LOGO_HOSPITAL_BASE64
        else ""
    )
    logo_university_html = (
        f"<img src='data:image/png;base64,{LOGO_UNIVERSITY_BASE64}' alt='University logo' style='max-width:72px; max-height:72px;'>"
        if LOGO_UNIVERSITY_BASE64
        else ""
    )

    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            :root {{
                --blue: #1f4e79;
                --border: #d7dee8;
                --muted: #5a6570;
                --bg: #ffffff;
            }}
            body {{
                font-family: Arial, Helvetica, sans-serif;
                background: var(--bg);
                color: #111827;
                margin: 0;
                padding: 16px;
            }}
            .toolbar {{
                margin-bottom: 14px;
            }}
            .print-btn {{
                background: var(--blue);
                color: white;
                border: none;
                padding: 10px 16px;
                border-radius: 8px;
                cursor: pointer;
                font-size: 14px;
                font-weight: 600;
            }}
            .report {{
                border: 1px solid var(--border);
                border-radius: 12px;
                padding: 18px;
            }}
            .header-grid {{
                display: grid;
                grid-template-columns: 84px 1fr 84px;
                align-items: center;
                column-gap: 12px;
                margin-bottom: 10px;
            }}
            .title-block {{
                text-align: center;
            }}
            .title-block h1 {{
                font-size: 24px;
                margin: 0 0 4px 0;
                color: var(--blue);
            }}
            .subtitle {{
                margin: 0 0 8px 0;
                font-size: 14px;
            }}
            .authors {{
                font-size: 12.5px;
                font-weight: 700;
                margin-bottom: 4px;
                line-height: 1.45;
            }}
            .affiliations {{
                font-size: 12.5px;
                line-height: 1.45;
            }}
            .meta {{
                margin-top: 14px;
                margin-bottom: 14px;
                padding: 12px;
                background: #f7fafc;
                border-radius: 10px;
                border: 1px solid var(--border);
                font-size: 13px;
                line-height: 1.6;
            }}
            h2 {{
                font-size: 18px;
                margin: 18px 0 8px 0;
                color: var(--blue);
            }}
            table {{
                width: 100%;
                border-collapse: collapse;
                margin-top: 8px;
            }}
            th, td {{
                border: 1px solid var(--border);
                padding: 8px 10px;
                vertical-align: top;
                font-size: 13px;
            }}
            th {{
                background: #eef4fb;
                text-align: left;
            }}
            .footer {{
                margin-top: 18px;
                color: var(--muted);
                font-size: 12px;
                line-height: 1.5;
            }}
            a {{
                color: var(--blue);
                text-decoration: none;
            }}
            @media print {{
                body {{
                    padding: 0;
                }}
                .toolbar {{
                    display: none;
                }}
                .report {{
                    border: none;
                    padding: 0;
                }}
            }}
        </style>
    </head>
    <body>
        <div class="toolbar">
            <button class="print-btn" onclick="window.print()">🖨 {html.escape(t(lang, 'print_report'))}</button>
        </div>

        <div class="report">
            <div class="header-grid">
                <div>{logo_hospital_html}</div>
                <div class="title-block">
                    <h1>{html.escape(t(lang, 'app_title'))}</h1>
                    <div class="subtitle">{html.escape(t(lang, 'report_title'))}</div>
                    <div class="authors">{html.escape(authors_text)}</div>
                    <div class="affiliations">{affiliations_html}</div>
                </div>
                <div style="text-align:right;">{logo_university_html}</div>
            </div>

            <div class="meta">
                <div><strong>{html.escape(t(lang, 'report_model'))}:</strong> {html.escape(model_text)}</div>
                <div><strong>{html.escape(t(lang, 'report_version'))}:</strong> {html.escape(APP_VERSION)}</div>
                <div><strong>{html.escape(t(lang, 'report_contact'))}:</strong> <a href="mailto:{html.escape(CONTACT_EMAIL)}">{html.escape(CONTACT_EMAIL)}</a></div>
                <div><strong>{html.escape(t(lang, 'report_datetime'))}:</strong> {html.escape(now_text)}</div>
            </div>

            <h2>{html.escape(t(lang, 'report_inputs'))}</h2>
            <table>
                <thead>
                    <tr>
                        <th>{html.escape(t(lang, 'report_parameter'))}</th>
                        <th>{html.escape(t(lang, 'report_value'))}</th>
                    </tr>
                </thead>
                <tbody>
                    {input_rows}
                </tbody>
            </table>

            <h2>{html.escape(t(lang, 'report_results'))}</h2>
            <table>
                <thead>
                    <tr>
                        <th>{html.escape(t(lang, 'report_parameter'))}</th>
                        <th>{html.escape(t(lang, 'report_value'))}</th>
                    </tr>
                </thead>
                <tbody>
                    {result_html}
                </tbody>
            </table>

            <div class="footer">{html.escape(FOOTER_NOTES[lang])}</div>
        </div>
    </body>
    </html>
    """


def render_printable_report(model_key: str, lang: str):
    result = st.session_state.get(f"result_{model_key}")
    values = st.session_state.get(f"inputs_{model_key}")
    if not result or not values:
        return

    st.markdown(f"### {t(lang, 'printable_report')}")
    st.caption(t(lang, "printable_report_caption"))

    report_html = build_print_report_html(model_key, lang)
    required_count = len(model_required_inputs(model_key))
    component_height = min(max(760 + 30 * required_count, 920), 1500)
    components.html(report_html, height=component_height, scrolling=True)


def show_result_panel(model_key: str, lang: str):
    result = st.session_state.get(f"result_{model_key}")
    model = MODELS[model_key]

    st.subheader(t(lang, "prediction"))

    if not result:
        st.info(t(lang, "enter_values_prompt"))
        return

    probability_pct = result["probability"] * 100.0
    st.metric(t(lang, "predicted_probability"), f"{probability_pct:.1f}%")
    st.progress(min(max(int(round(probability_pct)), 0), 100))

    if result["ci"] is not None:
        ci_low = result["ci"]["prob_low"] * 100.0
        ci_high = result["ci"]["prob_high"] * 100.0
        ci_connector = "to" if lang == "en" else "đến"
        st.write(f"**{t(lang, 'ci_label')}:** {ci_low:.1f}% {ci_connector} {ci_high:.1f}%")
        st.caption(t(lang, "ci_note"))
    else:
        st.caption(t(lang, "ci_not_available"))

    st.write(f"**{t(lang, 'linear_predictor')}:** {result['lp']:.4f}")

    if "lab_crp_model" in model["active_terms"]:
        st.write(f"**{t(lang, 'crp_transformed')}:** log(1 + CRP) = {result['transformed_crp']:.4f}")

    render_member_save_section(model_key, lang)

    with st.expander(t(lang, "show_contributions")):
        contrib = result["contributions"].copy()
        contrib["x_value"] = contrib["x_value"].map(lambda x: f"{x:.4f}")
        contrib["beta"] = contrib["beta"].map(lambda x: f"{x:.6f}")
        contrib["contribution"] = contrib["contribution"].map(lambda x: f"{x:.6f}")
        st.dataframe(
            contrib[["display", "x_value", "beta", "contribution"]],
            use_container_width=True,
            hide_index=True,
        )

    render_printable_report(model_key, lang)


def initialize_state():
    query_lang = get_query_param("lang")
    if query_lang in {"vi", "en"}:
        st.session_state["lang"] = query_lang
    elif "lang" not in st.session_state:
        st.session_state["lang"] = "vi"

    model_keys = list(MODELS.keys())
    query_model = get_query_param("model")
    if query_model in model_keys:
        st.session_state["selected_model"] = query_model
    elif "selected_model" not in st.session_state and model_keys:
        st.session_state["selected_model"] = model_keys[0]


def main():
    initialize_state()
    lang = st.session_state.get("lang", "vi")

    with st.sidebar:
        st.header(t(lang, "model_selection"))
        model_keys = list(MODELS.keys())
        st.selectbox(
            t(lang, "choose_model"),
            options=model_keys,
            format_func=lambda key: model_short_name(key, lang),
            key="selected_model",
        )
        model_key = st.session_state["selected_model"]
        sync_query_params(model_key=model_key, lang=lang)

        st.markdown("---")
        st.warning(t(lang, "research_warning"))
        st.caption(f"{version_text(lang)} · {contact_text(lang)}")

    render_header(lang)
    st.divider()
    render_guidance(lang)

    input_col, summary_col = st.columns([1.15, 0.85], gap="large")

    with input_col:
        st.subheader(t(lang, "input_form"))
        st.caption(t(lang, "input_form_caption"))

        required_inputs = model_required_inputs(model_key)
        section_to_inputs = defaultdict(list)
        for name in required_inputs:
            section_to_inputs[INPUT_DEFS[name]["section"]].append(name)

        with st.form(key=f"form_{model_key}"):
            collected_values = {}

            for section in SECTION_ORDER:
                section_inputs = section_to_inputs.get(section, [])
                if not section_inputs:
                    continue

                st.markdown(f"### {section_label(section, lang)}")
                cols = st.columns(2)
                for idx, input_name in enumerate(section_inputs):
                    with cols[idx % 2]:
                        collected_values[input_name] = render_widget(input_name, lang)

            submitted = st.form_submit_button(t(lang, "calculate_risk"), use_container_width=True)

        if submitted:
            warnings = validate_inputs(model_key, collected_values, lang)
            if warnings:
                for warning in warnings:
                    st.error(warning)
            else:
                st.session_state[f"inputs_{model_key}"] = collected_values
                st.session_state[f"result_{model_key}"] = predict(model_key, collected_values)
                st.success(t(lang, "risk_calculated"))

        show_result_panel(model_key, lang)

    with summary_col:
        show_model_summary(model_key, lang)

    st.divider()
    st.caption(f"{FOOTER_NOTES[lang]} · {version_text(lang)} · {contact_text(lang)}")


if __name__ == "__main__":
    main()
