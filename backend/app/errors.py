MESSAGES = {
    "REQUIRED_FIELD": "請填寫必要欄位", "INVALID_VALUE": "欄位值不合法",
    "EMPLOYEE_NOT_FOUND": "找不到所選員工", "INVALID_DATE": "請填寫有效日期 YYYY-MM-DD",
    "REVERSE_DATES": "結束日期不得早於開始日期", "HALF_DAY_SINGLE_DATE": "半天假限同一天",
    "NO_WORKDAYS": "申請期間沒有工作日", "REASON_TOO_LONG": "理由最多 200 字",
    "UNKNOWN_FIELD": "包含不支援的欄位", "DB_UNAVAILABLE": "資料庫暫時無法使用，請稍後再試",
    "SUBMISSION_UNKNOWN": "無法確認是否送出成功，請先查看我的假單，再決定是否重送",
    "INVALID_JSON": "請提供有效的 JSON", "UNSUPPORTED_MEDIA_TYPE": "請使用 JSON 格式送出",
    "NOT_FOUND": "找不到此 API", "METHOD_NOT_ALLOWED": "不支援此操作方法",
    "INTERNAL_ERROR": "系統暫時無法處理",
}


class DomainError(Exception):
    def __init__(self, code, field=None, status=422):
        self.code, self.field, self.status = code, field, status
        super().__init__(code)


class StorageUnavailable(DomainError):
    def __init__(self):
        super().__init__("DB_UNAVAILABLE", status=503)


class SubmissionUnknown(DomainError):
    def __init__(self):
        super().__init__("SUBMISSION_UNKNOWN", status=503)


def error_body(code, field=None):
    return {"error": {"code": code, "message": MESSAGES[code], "field": field}}
