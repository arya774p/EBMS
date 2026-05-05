import json
import time
from decimal import Decimal

from flask import g, has_request_context, request
from sqlalchemy import create_engine, event, text

from extensions import db
from models import SQLQueryLog


SENSITIVE_KEYS = {"password", "password_hash", "secret", "token"}


def ensure_query_log_table(app):
    with app.app_context():
        SQLQueryLog.__table__.create(db.engine, checkfirst=True)


def install_query_logger(app):
    logging_engine = create_engine(
        app.config["SQLALCHEMY_DATABASE_URI"],
        pool_pre_ping=True,
        isolation_level="AUTOCOMMIT",
    )
    app.extensions["sql_query_logging_engine"] = logging_engine

    with app.app_context():
        engine = db.engine
    if getattr(engine, "_ebms_query_logger_installed", False):
        return

    @event.listens_for(engine, "before_cursor_execute")
    def before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
        context._ebms_query_start = time.perf_counter()

    @event.listens_for(engine, "after_cursor_execute")
    def after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
        if should_skip_statement(statement):
            return
        duration_ms = (time.perf_counter() - context._ebms_query_start) * 1000
        write_query_log(logging_engine, statement, parameters, duration_ms, True, None)

    @event.listens_for(engine, "handle_error")
    def handle_error(exception_context):
        statement = exception_context.statement or ""
        if should_skip_statement(statement):
            return
        duration_ms = None
        if exception_context.execution_context is not None:
            started_at = getattr(exception_context.execution_context, "_ebms_query_start", None)
            if started_at is not None:
                duration_ms = (time.perf_counter() - started_at) * 1000
        write_query_log(
            logging_engine,
            statement,
            exception_context.parameters,
            duration_ms,
            False,
            str(exception_context.original_exception),
        )

    engine._ebms_query_logger_installed = True


def should_skip_statement(statement):
    lower_statement = (statement or "").lower()
    stripped = lower_statement.strip()
    if not stripped:
        return True
    if "sql_query_log" in lower_statement:
        return True
    if stripped.startswith(("show ", "set ", "select database", "select @@")):
        return True
    return False


def statement_type(statement):
    stripped = (statement or "").strip()
    if not stripped:
        return "UNKNOWN"
    return stripped.split(None, 1)[0].upper()[:20]


def request_context_values():
    if not has_request_context():
        return None, None, None, None
    return (
        getattr(g, "query_user_id", None),
        getattr(g, "query_user_role", None),
        request.path[:255],
        request.method[:10],
    )


def write_query_log(logging_engine, statement, parameters, duration_ms, success, error_message):
    user_id, user_role, route_path, http_method = request_context_values()
    values = {
        "user_id": user_id,
        "user_role": user_role,
        "route_path": route_path,
        "http_method": http_method,
        "statement_type": statement_type(statement),
        "query_text": normalize_statement(statement),
        "parameters_json": serialize_parameters(statement, parameters),
        "duration_ms": round(duration_ms, 3) if duration_ms is not None else None,
        "success": success,
        "error_message": (error_message or "")[:255] or None,
    }

    insert_sql = text(
        """
        INSERT INTO sql_query_log (
            user_id, user_role, route_path, http_method, statement_type,
            query_text, parameters_json, duration_ms, success, error_message
        )
        VALUES (
            :user_id, :user_role, :route_path, :http_method, :statement_type,
            :query_text, :parameters_json, :duration_ms, :success, :error_message
        )
        """
    )

    try:
        with logging_engine.connect() as connection:
            connection.execute(insert_sql, values)
    except Exception:
        # Query logging is educational support. It must never break the app flow.
        return


def normalize_statement(statement):
    return " ".join((statement or "").split())


def serialize_parameters(statement, parameters):
    if parameters is None:
        return None

    statement_mentions_sensitive_data = any(key in (statement or "").lower() for key in SENSITIVE_KEYS)
    safe_parameters = redact_parameters(parameters, statement_mentions_sensitive_data)

    try:
        return json.dumps(safe_parameters, default=json_default)[:60000]
    except TypeError:
        return json.dumps(str(safe_parameters))[:60000]


def redact_parameters(value, force_redact=False):
    if force_redact and not isinstance(value, dict):
        return "[REDACTED]"

    if isinstance(value, dict):
        redacted = {}
        for key, item in value.items():
            key_text = str(key).lower()
            if force_redact or any(sensitive_key in key_text for sensitive_key in SENSITIVE_KEYS):
                redacted[str(key)] = "[REDACTED]"
            else:
                redacted[str(key)] = redact_parameters(item)
        return redacted

    if isinstance(value, (list, tuple)):
        return [redact_parameters(item, force_redact) for item in value]

    return value


def json_default(value):
    if isinstance(value, Decimal):
        return str(value)
    return str(value)
