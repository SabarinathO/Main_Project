import smtplib

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
EMAIL_HOST_USER = "nexostudypartner@gmail.com"
EMAIL_HOST_PASSWORD = "eikd vuoe ecbw tpgo"  # Replace with your app password

# Test sending an email
server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
server.starttls()
server.login(EMAIL_HOST_USER, EMAIL_HOST_PASSWORD)
server.sendmail(EMAIL_HOST_USER, "recipient_email@example.com", "Subject: Test Email\n\nThis is a test email.")
server.quit()

print("Email sent successfully!")
