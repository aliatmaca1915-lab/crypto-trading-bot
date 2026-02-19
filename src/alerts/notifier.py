"""
Alert and Notification System
Sends alerts via email, Telegram, and Discord
"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import requests
from typing import Dict, Optional
from datetime import datetime


class AlertSystem:
    """Send alerts and notifications"""
    
    def __init__(self, config=None):
        """Initialize alert system"""
        self.config = config
        
        # Email configuration
        self.email_enabled = config.get('notifications.email.enabled', False) if config else False
        if self.email_enabled:
            self.smtp_server = config.get('notifications.email.smtp_server')
            self.smtp_port = config.get('notifications.email.smtp_port')
            self.sender_email = config.get('notifications.email.sender_email')
            self.sender_password = config.get('notifications.email.sender_password')
            self.recipient_email = config.get('notifications.email.recipient_email')
        
        # Telegram configuration
        self.telegram_enabled = config.get('notifications.telegram.enabled', False) if config else False
        if self.telegram_enabled:
            self.telegram_token = config.get('notifications.telegram.bot_token')
            self.telegram_chat_id = config.get('notifications.telegram.chat_id')
        
        # Discord configuration
        self.discord_enabled = config.get('notifications.discord.enabled', False) if config else False
        if self.discord_enabled:
            self.discord_webhook = config.get('notifications.discord.webhook_url')
    
    def send_trade_alert(self, trade_info: Dict):
        """
        Send alert for new trade
        
        Args:
            trade_info: Dictionary with trade information
        """
        subject = f"🚀 New Trade: {trade_info.get('symbol', 'Unknown')}"
        
        message = f"""
New Trade Opened
================
Symbol: {trade_info.get('symbol', 'N/A')}
Side: {trade_info.get('side', 'N/A').upper()}
Classification: {trade_info.get('classification', 'N/A')}
Score: {trade_info.get('score', 0)}/100

Entry Price: ${trade_info.get('entry_price', 0):.2f}
Quantity: {trade_info.get('quantity', 0):.6f}
Position Value: ${trade_info.get('position_value', 0):,.2f}
Leverage: {trade_info.get('leverage', 1)}x

Stop Loss: ${trade_info.get('stop_loss', 0):.2f}
Take Profit: ${trade_info.get('take_profit', 0):.2f}

Mode: {trade_info.get('mode', 'paper').upper()}
Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        
        self._send_notification(subject, message)
    
    def send_position_closed_alert(self, position_info: Dict):
        """
        Send alert when position is closed
        
        Args:
            position_info: Dictionary with position information
        """
        pnl = position_info.get('realized_pnl', 0)
        emoji = "✅" if pnl > 0 else "❌"
        
        subject = f"{emoji} Position Closed: {position_info.get('symbol', 'Unknown')}"
        
        message = f"""
Position Closed
===============
Symbol: {position_info.get('symbol', 'N/A')}
Classification: {position_info.get('classification', 'N/A')}

Entry Price: ${position_info.get('entry_price', 0):.2f}
Exit Price: ${position_info.get('exit_price', 0):.2f}
Quantity: {position_info.get('quantity', 0):.6f}

Realized P&L: ${pnl:,.2f} ({pnl/position_info.get('position_value', 1)*100:+.2f}%)
Reason: {position_info.get('exit_reason', 'Manual')}

Mode: {position_info.get('mode', 'paper').upper()}
Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        
        self._send_notification(subject, message)
    
    def send_risk_alert(self, risk_info: Dict):
        """
        Send risk alert
        
        Args:
            risk_info: Dictionary with risk information
        """
        subject = f"⚠️ Risk Alert: {risk_info.get('type', 'Unknown')}"
        
        message = f"""
RISK ALERT
==========
Type: {risk_info.get('type', 'Unknown')}
Severity: {risk_info.get('severity', 'Medium').upper()}

Details:
{risk_info.get('details', 'No details provided')}

Current Capital: ${risk_info.get('current_capital', 0):,.2f}
Max Drawdown: {risk_info.get('max_drawdown', 0)*100:.2f}%

Action Required: {risk_info.get('action_required', 'Monitor situation')}

Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        
        self._send_notification(subject, message, priority='high')
    
    def send_system_alert(self, system_info: Dict):
        """
        Send system alert
        
        Args:
            system_info: Dictionary with system information
        """
        subject = f"🔧 System Alert: {system_info.get('type', 'Unknown')}"
        
        message = f"""
SYSTEM ALERT
============
Type: {system_info.get('type', 'Unknown')}
Status: {system_info.get('status', 'Unknown')}

Message:
{system_info.get('message', 'No message provided')}

Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        
        self._send_notification(subject, message)
    
    def send_daily_summary(self, summary: Dict):
        """
        Send daily performance summary
        
        Args:
            summary: Dictionary with daily summary
        """
        subject = f"📊 Daily Summary - {summary.get('date', 'Today')}"
        
        pnl = summary.get('total_pnl', 0)
        emoji = "📈" if pnl > 0 else "📉"
        
        message = f"""
{emoji} DAILY PERFORMANCE SUMMARY
==============================
Date: {summary.get('date', 'N/A')}

Trading Activity:
- Total Trades: {summary.get('total_trades', 0)}
- Closed Trades: {summary.get('closed_trades', 0)}
- Win Rate: {summary.get('win_rate', 0):.1f}%

Profit & Loss:
- Total P&L: ${pnl:,.2f}
- Daily Return: {summary.get('daily_return_pct', 0):+.2f}%
- Average Win: ${summary.get('average_win', 0):,.2f}
- Average Loss: ${summary.get('average_loss', 0):,.2f}

Capital:
- Current Capital: ${summary.get('current_capital', 0):,.2f}
- Capital Change: ${summary.get('capital_change', 0):+,.2f}

Mode: {summary.get('mode', 'paper').upper()}
"""
        
        self._send_notification(subject, message)
    
    def _send_notification(self, subject: str, message: str, priority: str = 'normal'):
        """
        Send notification via all enabled channels
        
        Args:
            subject: Notification subject
            message: Notification message
            priority: Priority level ('low', 'normal', 'high')
        """
        # Send email
        if self.email_enabled:
            try:
                self._send_email(subject, message)
            except Exception as e:
                print(f"Failed to send email: {e}")
        
        # Send Telegram
        if self.telegram_enabled:
            try:
                self._send_telegram(f"{subject}\n\n{message}")
            except Exception as e:
                print(f"Failed to send Telegram message: {e}")
        
        # Send Discord
        if self.discord_enabled:
            try:
                self._send_discord(subject, message)
            except Exception as e:
                print(f"Failed to send Discord message: {e}")
    
    def _send_email(self, subject: str, body: str):
        """Send email notification"""
        msg = MIMEMultipart()
        msg['From'] = self.sender_email
        msg['To'] = self.recipient_email
        msg['Subject'] = subject
        
        msg.attach(MIMEText(body, 'plain'))
        
        with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
            server.starttls()
            server.login(self.sender_email, self.sender_password)
            server.send_message(msg)
    
    def _send_telegram(self, message: str):
        """Send Telegram notification"""
        url = f"https://api.telegram.org/bot{self.telegram_token}/sendMessage"
        
        payload = {
            'chat_id': self.telegram_chat_id,
            'text': message,
            'parse_mode': 'HTML'
        }
        
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
    
    def _send_discord(self, title: str, description: str):
        """Send Discord notification"""
        payload = {
            'embeds': [{
                'title': title,
                'description': description,
                'color': 3447003,  # Blue
                'timestamp': datetime.now().isoformat()
            }]
        }
        
        response = requests.post(
            self.discord_webhook,
            json=payload,
            timeout=10
        )
        response.raise_for_status()
