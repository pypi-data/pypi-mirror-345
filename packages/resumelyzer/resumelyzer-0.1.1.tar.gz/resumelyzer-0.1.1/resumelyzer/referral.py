# referral.py
from typing import Dict
import sqlite3
from datetime import datetime, timedelta

class ReferralTracker:
    def __init__(self, db_path: str = "referrals.db"):
        self.conn = sqlite3.connect(db_path)
        self._init_db()
    
    def _init_db(self):
        self.conn.execute("""
        CREATE TABLE IF NOT EXISTS referrals (
            referrer_id TEXT,
            referred_email TEXT,
            referral_date TEXT,
            is_verified INTEGER DEFAULT 0,
            PRIMARY KEY (referrer_id, referred_email)
        )
        """)
        self.conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id TEXT PRIMARY KEY,
            email TEXT,
            pro_expiry TEXT
        )
        """)
        self.conn.commit()
    
    def track_referral(self, referrer_id: str, referred_email: str):
        self.conn.execute(
            "INSERT OR IGNORE INTO referrals VALUES (?, ?, ?, 0)",
            (referrer_id, referred_email, datetime.now().isoformat())
        )
        self.conn.commit()
    
    def verify_referrals(self, referred_email: str):
        self.conn.execute(
            "UPDATE referrals SET is_verified = 1 WHERE referred_email = ?",
            (referred_email,)
        )
        self.conn.commit()
        
        # Count verified referrals
        cur = self.conn.cursor()
        cur.execute("""
        SELECT referrer_id, COUNT(*) 
        FROM referrals 
        WHERE is_verified = 1 
        GROUP BY referrer_id
        """)
        return cur.fetchall()
    
    def apply_referral_credits(self):
        referrals = self.verify_referrals()
        for referrer_id, count in referrals:
            if count >= 3:
                # Apply 1 month pro credit
                cur = self.conn.execute(
                    "SELECT pro_expiry FROM users WHERE user_id = ?",
                    (referrer_id,)
                )
                expiry = cur.fetchone()
                new_expiry = self._calculate_new_expiry(expiry)
                self.conn.execute(
                    "UPDATE users SET pro_expiry = ? WHERE user_id = ?",
                    (new_expiry.isoformat(), referrer_id)
                )
                self.conn.commit()
    
    def _calculate_new_expiry(self, current_expiry):
        if not current_expiry:
            return datetime.now() + timedelta(days=30)
        expiry_date = datetime.fromisoformat(current_expiry)
        if expiry_date < datetime.now():
            return datetime.now() + timedelta(days=30)
        return expiry_date + timedelta(days=30)