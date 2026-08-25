import smtplib
import logging
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime, timezone
from constants import SMTP_USER, SMTP_PASSWORD, ALERT_EMAIL

logger = logging.getLogger(__name__)

_SMTP_HOST = "smtp.gmail.com"
_SMTP_PORT = 587


def send_alert(process_name: str, pid: int, cpu_pct: float, mem_pct: float, duration_secs: int):
    if not (SMTP_USER and SMTP_PASSWORD and ALERT_EMAIL):
        logger.warning("Email alert skipped: SMTP_USER/SMTP_PASSWORD/ALERT_EMAIL not configured")
        return

    subject = f"⚠️ ProcessAI Alert: {process_name} is using {cpu_pct:.1f}% CPU"
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

    html = f"""
    <html><body style="font-family:Arial,sans-serif;color:#0f172a;background:#f5f7fa;margin:0;padding:24px;">
      <div style="max-width:520px;margin:0 auto;background:#ffffff;border:1px solid #e2e8f0;
                  border-radius:8px;padding:32px;">
        <h2 style="margin:0 0 8px;font-size:18px;color:#dc2626;">&#9888;&#65039; High CPU Alert</h2>
        <p style="margin:0 0 24px;font-size:13px;color:#64748b;">
          ProcessAI detected a HIGH-severity anomaly on your system.
        </p>
        <table width="100%" cellpadding="10" cellspacing="0"
               style="border-collapse:collapse;font-size:13px;">
          <thead>
            <tr style="background:#f8fafc;">
              <th style="text-align:left;border:1px solid #e2e8f0;color:#64748b;
                         font-weight:600;text-transform:uppercase;font-size:11px;
                         letter-spacing:0.05em;">Field</th>
              <th style="text-align:left;border:1px solid #e2e8f0;color:#64748b;
                         font-weight:600;text-transform:uppercase;font-size:11px;
                         letter-spacing:0.05em;">Value</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td style="border:1px solid #e2e8f0;color:#64748b;">Process</td>
              <td style="border:1px solid #e2e8f0;font-weight:600;">{process_name}</td>
            </tr>
            <tr style="background:#f8fafc;">
              <td style="border:1px solid #e2e8f0;color:#64748b;">PID</td>
              <td style="border:1px solid #e2e8f0;">{pid}</td>
            </tr>
            <tr>
              <td style="border:1px solid #e2e8f0;color:#64748b;">CPU Usage</td>
              <td style="border:1px solid #e2e8f0;color:#dc2626;font-weight:600;">{cpu_pct:.1f}%</td>
            </tr>
            <tr style="background:#f8fafc;">
              <td style="border:1px solid #e2e8f0;color:#64748b;">Memory Usage</td>
              <td style="border:1px solid #e2e8f0;">{mem_pct:.2f}%</td>
            </tr>
            <tr>
              <td style="border:1px solid #e2e8f0;color:#64748b;">Duration</td>
              <td style="border:1px solid #e2e8f0;">{duration_secs}s</td>
            </tr>
            <tr style="background:#f8fafc;">
              <td style="border:1px solid #e2e8f0;color:#64748b;">Detected at</td>
              <td style="border:1px solid #e2e8f0;">{timestamp}</td>
            </tr>
          </tbody>
        </table>
        <p style="margin:24px 0 0;font-size:12px;color:#94a3b8;">
          Sent by ProcessAI &mdash; Process Anomaly Monitor
        </p>
      </div>
    </body></html>
    """

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = SMTP_USER
    msg["To"] = ALERT_EMAIL
    msg.attach(MIMEText(html, "html"))

    try:
        with smtplib.SMTP(_SMTP_HOST, _SMTP_PORT, timeout=10) as server:
            server.ehlo()
            server.starttls()
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.sendmail(SMTP_USER, ALERT_EMAIL, msg.as_string())
        logger.info("Alert email sent for %s (PID %d)", process_name, pid)
    except Exception as exc:
        logger.error("Failed to send alert email for %s (PID %d): %s", process_name, pid, exc)
