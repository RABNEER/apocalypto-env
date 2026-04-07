def load_scam_scenarios() -> list[dict]:
    """Provides rich, localized financial fraud scenarios with strict ground truth."""
    return [
        {
            "id": "scenario_001",
            "initial_message": "URGENT: Your HDFC bank account will be blocked today due to pending KYC. Click here http://hdfc-kyc-update.xyz to update via your PhonePe UPI immediately. Call +91 9876543210 if any issues.",
            "ground_truth": {
                "label": "scam",
                "scam_type": "kyc_scam",
                "upi_ids": [],
                "phone_numbers": ["+91 9876543210"],
                "urls": ["http://hdfc-kyc-update.xyz"],
                "bank_accounts": [],
                "urgency_phrases": ["URGENT", "blocked today", "immediately"]
            },
            "hidden_intel": {
                "upi_id": "kycupdate@ybl",
                "bank_account": "50100456000089",
                "ifsc": "HDFC0000001",
                "phone": "9876543210"
            }
        },
        {
            "id": "scenario_002",
            "initial_message": "Congratulations! You won ₹25,00,000 in the Jio Lottery. To claim your prize money, pay processing fee of ₹12,500 to our manager 888 888 8888. Do not share this message.",
            "ground_truth": {
                "label": "scam",
                "scam_type": "lottery",
                "upi_ids": [],
                "phone_numbers": ["888 888 8888"],
                "urls": [],
                "bank_accounts": [],
                "urgency_phrases": ["To claim your prize money"]
            },
            "hidden_intel": {
                "upi_id": "jiolotto@sbi",
                "bank_account": "112233445566",
                "ifsc": "SBIN0000002",
                "phone": "8888888888"
            }
        },
        {
            "id": "scenario_003",
            "initial_message": "Hi Sir, I am calling from Mumbai Police Cyber Cell. A parcel under your name was intercepted containing illegal passports. Provide your bank details immediately for verification or face arrest.",
            "ground_truth": {
                "label": "scam",
                "scam_type": "impersonation",
                "upi_ids": [],
                "phone_numbers": [],
                "urls": [],
                "bank_accounts": [],
                "urgency_phrases": ["immediately", "face arrest"]
            },
            "hidden_intel": {
                "upi_id": "policeverified@okicici",
                "bank_account": "334455667788",
                "ifsc": "ICIC0000003",
                "phone": "9123456789"
            }
        },
        {
            "id": "scenario_004",
            "initial_message": "Action Required: Your electricity bill for last month is unpaid. Connection will be disconnected at 9 PM tonight. Pay immediately using this link http://power-reconnect.in/pay or call 9812345678.",
            "ground_truth": {
                "label": "scam",
                "scam_type": "upi_fraud",
                "upi_ids": [],
                "phone_numbers": ["9812345678"],
                "urls": ["http://power-reconnect.in/pay"],
                "bank_accounts": [],
                "urgency_phrases": ["Action Required", "9 PM tonight", "immediately"]
            },
            "hidden_intel": {
                "upi_id": "billpay@oksbi",
                "bank_account": "991188223344",
                "ifsc": "SBIN0001234",
                "phone": "9812345678"
            }
        },
        {
            "id": "scenario_005",
            "initial_message": "Dear customer, you have received a refund of ₹4,999 from Income Tax Dept. To credit into your bank, please verify your account at http://it-refund-portal.me/verify.",
            "ground_truth": {
                "label": "scam",
                "scam_type": "phishing",
                "upi_ids": [],
                "phone_numbers": [],
                "urls": ["http://it-refund-portal.me/verify"],
                "bank_accounts": [],
                "urgency_phrases": ["please verify your account"]
            },
            "hidden_intel": {
                "upi_id": "itaxrefund@paytm",
                "bank_account": "334455667788",
                "ifsc": "PYTM0123456",
                "phone": "9988776655"
            }
        },
        {
            "id": "scenario_006",
            "initial_message": "Urgent Job Opening! Amazon WFH Data Entry roles available. Salary ₹35,000/month. For registration, pay security deposit of ₹2,000 to +91 9900887766 UPI ID amzn-jobs@axl.",
            "ground_truth": {
                "label": "scam",
                "scam_type": "job_offer",
                "upi_ids": ["amzn-jobs@axl"],
                "phone_numbers": ["+91 9900887766"],
                "urls": [],
                "bank_accounts": [],
                "urgency_phrases": ["Urgent Job Opening"]
            },
            "hidden_intel": {
                "upi_id": "recruiters@okaxis",
                "bank_account": "50200088776655",
                "ifsc": "UTIB0000888",
                "phone": "9900887766"
            }
        },
        {
            "id": "scenario_007",
            "initial_message": "Pre-approved Loan of ₹5,00,000! No documentation required. Instant credit to your bank. Download App now: http://fast-loan-app.xyz or contact +91 9122334455.",
            "ground_truth": {
                "label": "scam",
                "scam_type": "loan_shark",
                "upi_ids": [],
                "phone_numbers": ["+91 9122334455"],
                "urls": ["http://fast-loan-app.xyz"],
                "bank_accounts": [],
                "urgency_phrases": ["No documentation required", "Instant credit"]
            },
            "hidden_intel": {
                "upi_id": "loanapproval@gpay",
                "bank_account": "1002003004005",
                "ifsc": "HDFC0001234",
                "phone": "9122334455"
            }
        },
        {
            "id": "scenario_008",
            "initial_message": "SBI Security Alert: Your Internet Banking access is suspended due to suspicious activity. Reactivate now by logging in at http://sbi-secure-portal.co.in/login.",
            "ground_truth": {
                "label": "scam",
                "scam_type": "phishing",
                "upi_ids": [],
                "phone_numbers": [],
                "urls": ["http://sbi-secure-portal.co.in/login"],
                "bank_accounts": [],
                "urgency_phrases": ["suspended", "Reactivate now"]
            },
            "hidden_intel": {
                "upi_id": "sbisafe@oksbi",
                "bank_account": "203040506070",
                "ifsc": "SBIN0005544",
                "phone": "9800776655"
            }
        },
        {
            "id": "scenario_009",
            "initial_message": "Earn ₹5,000 daily by liking YouTube videos! No experience needed. Join our Telegram group for payment: http://t.me/daily-earnings-hub or WhatsApp 9654321098.",
            "ground_truth": {
                "label": "scam",
                "scam_type": "job_offer",
                "upi_ids": [],
                "phone_numbers": ["9654321098"],
                "urls": ["http://t.me/daily-earnings-hub"],
                "bank_accounts": [],
                "urgency_phrases": ["Earn ₹5,000 daily", "No experience needed"]
            },
            "hidden_intel": {
                "upi_id": "youtubepayout@ybl",
                "bank_account": "556677889900",
                "ifsc": "YBLK0000999",
                "phone": "9654321098"
            }
        },
        {
            "id": "scenario_010",
            "initial_message": "KBC Lottery Winner! Your mobile number has won ₹15 Lakhs in our lucky draw. To claim prize, contact Mr. Rana Pratap on 9191928282 and pay file charges ₹9,999.",
            "ground_truth": {
                "label": "scam",
                "scam_type": "lottery",
                "upi_ids": [],
                "phone_numbers": ["9191928282"],
                "urls": [],
                "bank_accounts": [],
                "urgency_phrases": ["claim prize", "contact Mr. Rana Pratap"]
            },
            "hidden_intel": {
                "upi_id": "kbcrefill@okicici",
                "bank_account": "998877665544",
                "ifsc": "ICIC0001122",
                "phone": "9191928282"
            }
        },
        {
            "id": "scenario_011",
            "initial_message": "Urgent from Airtel: Your SIM card will be deactivated in 24 hours. Update your profile immediately at http://airtel-sim-kyc.net to avoid disconnection.",
            "ground_truth": {
                "label": "scam",
                "scam_type": "kyc_scam",
                "upi_ids": [],
                "phone_numbers": [],
                "urls": ["http://airtel-sim-kyc.net"],
                "bank_accounts": [],
                "urgency_phrases": ["deactivated in 24 hours", "immediately"]
            },
            "hidden_intel": {
                "upi_id": "airtelkyc@paytm",
                "bank_account": "778899001122",
                "ifsc": "PYTM0112233",
                "phone": "9771122334"
            }
        },
        {
            "id": "scenario_012",
            "initial_message": "Immediate Cash Loan up to ₹2 Lakhs! Just provide Aadhar and PAN. Low interest 1%. Call our executive 9001122334 for instant disbursement.",
            "ground_truth": {
                "label": "scam",
                "scam_type": "loan_shark",
                "upi_ids": [],
                "phone_numbers": ["9001122334"],
                "urls": [],
                "bank_accounts": [],
                "urgency_phrases": ["Immediate Cash Loan", "instant disbursement"]
            },
            "hidden_intel": {
                "upi_id": "cashloan@okaxis",
                "bank_account": "123123123123",
                "ifsc": "ICIC0006789",
                "phone": "9001122334"
            }
        },
        {
            "id": "scenario_013",
            "initial_message": "PhonePe Reward! You have won a cashback of ₹1,999. Click below link to swipe and claim your reward directly in your bank account: http://phonepe-reward-win.in.",
            "ground_truth": {
                "label": "scam",
                "scam_type": "upi_fraud",
                "upi_ids": [],
                "phone_numbers": [],
                "urls": ["http://phonepe-reward-win.in"],
                "bank_accounts": [],
                "urgency_phrases": ["swipe and claim your reward"]
            },
            "hidden_intel": {
                "upi_id": "rewardzone@ybl",
                "bank_account": "445566778899",
                "ifsc": "BARB0VADODR",
                "phone": "9887766554"
            }
        },
        {
            "id": "scenario_014",
            "initial_message": "Amazon Seller Support: Your seller account is reported for selling fake items. Verify your identity at http://amazon-seller-verify.biz within 1 hour or your payouts will be frozen.",
            "ground_truth": {
                "label": "scam",
                "scam_type": "impersonation",
                "upi_ids": [],
                "phone_numbers": [],
                "urls": ["http://amazon-seller-verify.biz"],
                "bank_accounts": [],
                "urgency_phrases": ["within 1 hour", "payouts will be frozen"]
            },
            "hidden_intel": {
                "upi_id": "amazonsupport@okaxis",
                "bank_account": "667788990011",
                "ifsc": "UTIB0001010",
                "phone": "9020102030"
            }
        },
        {
            "id": "scenario_015",
            "initial_message": "PAN Card Update Required: Your PAN will be inactive from tomorrow. Update your details using the NSDL link below: http://nsdl-pan-update.com/form.",
            "ground_truth": {
                "label": "scam",
                "scam_type": "kyc_scam",
                "upi_ids": [],
                "phone_numbers": [],
                "urls": ["http://nsdl-pan-update.com/form"],
                "bank_accounts": [],
                "urgency_phrases": ["inactive from tomorrow", "Update your details"]
            },
            "hidden_intel": {
                "upi_id": "nsdlupdate@oksbi",
                "bank_account": "889900112233",
                "ifsc": "SBIN0008899",
                "phone": "9911223344"
            }
        },
        {
            "id": "scenario_016",
            "initial_message": "URGENT: Your PNB Bank Debit card is blocked for security. Please call our 24x7 helpline 9776655443 to unblock and verify your CVV/Expiry details immediately.",
            "ground_truth": {
                "label": "scam",
                "scam_type": "upi_fraud",
                "upi_ids": [],
                "phone_numbers": ["9776655443"],
                "urls": [],
                "bank_accounts": [],
                "urgency_phrases": ["blocked for security", "immediately"]
            },
            "hidden_intel": {
                "upi_id": "pnbhelpdesk@oksbi",
                "bank_account": "112211221122",
                "ifsc": "PUNB0112200",
                "phone": "9776655443"
            }
        },
        {
            "id": "scenario_017",
            "initial_message": "Special Job Offer from Flipkart! Work just 2 hours a day and earn ₹2,500 daily. WhatsApp +91 9554433221 to start now. Registration fee required ₹499.",
            "ground_truth": {
                "label": "scam",
                "scam_type": "job_offer",
                "upi_ids": [],
                "phone_numbers": ["+91 9554433221"],
                "urls": [],
                "bank_accounts": [],
                "urgency_phrases": ["earn ₹2,500 daily", "Registration fee required"]
            },
            "hidden_intel": {
                "upi_id": "fkt-jobs@ybl",
                "bank_account": "990011223344",
                "ifsc": "KKBK0001010",
                "phone": "9554433221"
            }
        },
        {
            "id": "scenario_018",
            "initial_message": "Free iPhone 15 Pro! Only 3 left. Pay just ₹999 shipping charges to claim your free reward. Use this exclusive UPI link: http://win-iphone.pro/pay or pay to +91 9443322110.",
            "ground_truth": {
                "label": "scam",
                "scam_type": "lottery",
                "upi_ids": [],
                "phone_numbers": ["+91 9443322110"],
                "urls": ["http://win-iphone.pro/pay"],
                "bank_accounts": [],
                "urgency_phrases": ["Only 3 left", "claim your free reward"]
            },
            "hidden_intel": {
                "upi_id": "shippingsales@okicici",
                "bank_account": "443322114433",
                "ifsc": "ICIC0004433",
                "phone": "9443322110"
            }
        },
        {
            "id": "scenario_019",
            "initial_message": "Need Gold Loan? Get cash against gold in 10 minutes. No proof needed. Low interest 0.5%. Call Mr. Gupta 9332211006 for immediate pickup.",
            "ground_truth": {
                "label": "scam",
                "scam_type": "loan_shark",
                "upi_ids": [],
                "phone_numbers": ["9332211006"],
                "urls": [],
                "bank_accounts": [],
                "urgency_phrases": ["in 10 minutes", "immediate pickup"]
            },
            "hidden_intel": {
                "upi_id": "goldloan@paytm",
                "bank_account": "665544332211",
                "ifsc": "PYTM0001122",
                "phone": "9332211006"
            }
        },
        {
            "id": "scenario_020",
            "initial_message": "Your OLX listing has a buyer! To receive ₹12,000 for your furniture, click this link to verify and accept payment: http://olx-payout.in/Furniture-9988.",
            "ground_truth": {
                "label": "scam",
                "scam_type": "upi_fraud",
                "upi_ids": [],
                "phone_numbers": [],
                "urls": ["http://olx-payout.in/Furniture-9988"],
                "bank_accounts": [],
                "urgency_phrases": ["To receive ₹12,000", "accept payment"]
            },
            "hidden_intel": {
                "upi_id": "olxbuyer@aks",
                "bank_account": "887766554433",
                "ifsc": "AXIS0009988",
                "phone": "9080706050"
            }
        }
    ]
