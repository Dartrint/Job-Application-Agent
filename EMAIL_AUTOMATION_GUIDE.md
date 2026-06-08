# 📧 Email Automation Guide / Hướng Dẫn Gửi Email Tự Động

## English Version

### Overview

The Job Application Agent can automatically email analysis reports (HTML + JSON) to one or more recipients. This guide walks you through setup and usage.

### Features

- **Automatic Report Generation** - Creates HTML and JSON reports after analysis
- **Email Delivery** - Sends reports to configured email addresses
- **Scheduled Sending** - Enable `AUTO_SEND_REPORT=true` to email from every run
- **Custom Recipients** - Override recipient email via CLI flag
- **Attachment Support** - Both HTML and JSON reports attached to email

---

## Step 1: Get Gmail App Password

If using Gmail (recommended), you need an **App Password**, not your regular Gmail password.

### For Gmail Users:

1. Go to [myaccount.google.com/security](https://myaccount.google.com/security)
2. Enable **2-Step Verification** (if not already enabled)
3. Go to [myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords)
4. Select **Mail** and **Windows Computer** (or your device)
5. Google will generate a 16-character password
6. Copy this password (you'll use it in `.env`)

### For Other Email Providers:

- **Outlook/Hotmail**: Use your regular password with `smtp-mail.outlook.com`
- **Yahoo**: Use App Password from [account.yahoo.com/security](https://account.yahoo.com/security)
- **Custom Domain**: Check your email provider's SMTP settings

---

## Step 2: Configure `.env` File

Edit your `.env` file and fill in the email settings:

```bash
# Email / Automation (required for --email and automation.py)
SMTP_HOST=smtp.gmail.com           # Gmail: smtp.gmail.com
SMTP_PORT=587                      # Standard: 587 (TLS)
SMTP_USER=your_email@gmail.com     # Your email address
SMTP_PASSWORD=your_app_password    # Gmail App Password (16 chars)
SMTP_USE_TLS=true                  # Use TLS encryption
REPORT_EMAIL_FROM=your_email@gmail.com    # Sender address (usually same as SMTP_USER)
REPORT_EMAIL_TO=recipient@example.com     # Default recipient
AUTO_SEND_REPORT=false             # Set to 'true' to always email results
```

### Configuration Reference

| Setting | Example | Description |
|---------|---------|-------------|
| `SMTP_HOST` | smtp.gmail.com | SMTP server address |
| `SMTP_PORT` | 587 | SMTP port (587 for TLS, 465 for SSL) |
| `SMTP_USER` | user@gmail.com | Email account for authentication |
| `SMTP_PASSWORD` | xxxx xxxx xxxx xxxx | App password (not regular password) |
| `SMTP_USE_TLS` | true | Enable TLS encryption |
| `REPORT_EMAIL_FROM` | user@gmail.com | Sender email address |
| `REPORT_EMAIL_TO` | recipient@example.com | Default recipient email |
| `AUTO_SEND_REPORT` | false | Auto-send on every run (true/false) |

---

## Step 3: Test Email Configuration

Run a quick test to verify your setup:

```bash
# Test with sample data and email
python automation.py --demo --email

# Expected output:
# [OK] Job Analysis
# [OK] CV Analysis
# [OK] Interview Prep
# [OK] Cover Letter
# Reports saved:
#   HTML: reports/report_XXXXXX.html
#   JSON: reports/report_XXXXXX.json
#   Duration: X.Xs
#   Email sent to: recipient@example.com
```

---

## Step 4: Usage Examples

### Option A: Email on Demand (Recommended for Testing)

Send email only when you use the `--email` flag:

```bash
# Demo with email
python automation.py --demo --email

# With your files
python automation.py job_description.pdf resume.pdf --email

# To custom recipient
python automation.py examples/sample_job.txt examples/sample_cv.txt --email-to boss@company.com
```

### Option B: Automatic Email (Set AUTO_SEND_REPORT=true)

Enable automatic emailing for every analysis:

```bash
# Edit .env
AUTO_SEND_REPORT=true

# Now every run sends email automatically
python automation.py --demo
python automation.py job_description.pdf resume.pdf

# Skip email if needed
python automation.py --demo --no-email
```

### Option C: Web UI with Email

```bash
streamlit run app.py
```

Then in the sidebar, when email is configured, you'll see a checkbox: "Send report to email"

---

## Email Template

The email sent contains:

**Subject:** Job Application Analysis Report

**Body:** 
- Professional HTML formatted report
- Includes all analysis sections:
  - Job Profile Summary
  - CV Match Score & Recommendations
  - Interview Preparation Guide
  - Cover Letter Variations

**Attachments:**
- `report_XXXXXX.html` - Formatted HTML report
- `report_XXXXXX.json` - Raw JSON data for processing

---

## Troubleshooting

| Error | Cause | Solution |
|-------|-------|----------|
| `SMTP authentication failed` | Wrong password or app password | Use Gmail App Password, not regular password |
| `Connection timeout` | SMTP host unreachable | Check SMTP_HOST and SMTP_PORT values |
| `Email not sending` | EMAIL_ENABLED=false | Verify all 4 required fields are set |
| `Connection refused` | Firewall blocking port 587 | Check your firewall or ISP settings |
| `Email is not configured` | Missing required env vars | Fill all 4 fields: SMTP_HOST, SMTP_USER, SMTP_PASSWORD, REPORT_EMAIL_TO |

---

## Security Best Practices

⚠️ **Never commit `.env` file to Git**
- Add `.env` to `.gitignore`
- Keep `.env` passwords private
- Use environment variables in production

✅ **Gmail Security:**
- Use App Passwords, not your main password
- Keep your 2-Step Verification enabled
- Revoke app passwords when no longer needed

---

---

## Phiên Bản Tiếng Việt

### Tổng Quan

Job Application Agent có thể tự động gửi email báo cáo phân tích (HTML + JSON) đến các địa chỉ nhận được cấu hình. Hướng dẫn này sẽ hướng dẫn bạn cách thiết lập và sử dụng.

### Tính Năng

- **Tạo báo cáo tự động** - Tạo báo cáo HTML và JSON sau khi phân tích
- **Gửi Email** - Gửi báo cáo đến các địa chỉ email được cấu hình
- **Gửi Lên Lịch** - Bật `AUTO_SEND_REPORT=true` để gửi email từ mỗi lần chạy
- **Người nhận tùy chỉnh** - Ghi đè email nhận qua lệnh CLI
- **Hỗ trợ đính kèm** - Cả báo cáo HTML và JSON được đính kèm vào email

---

## Bước 1: Lấy Mật Khẩu Ứng Dụng Gmail

Nếu sử dụng Gmail (được khuyến nghị), bạn cần **Mật Khẩu Ứng Dụng**, không phải mật khẩu Gmail thông thường.

### Cho Người Dùng Gmail:

1. Truy cập [myaccount.google.com/security](https://myaccount.google.com/security)
2. Bật **Xác Minh Hai Bước** (nếu chưa bật)
3. Truy cập [myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords)
4. Chọn **Mail** và **Windows Computer** (hoặc thiết bị của bạn)
5. Google sẽ tạo một mật khẩu 16 ký tự
6. Sao chép mật khẩu này (bạn sẽ sử dụng nó trong `.env`)

### Cho Các Nhà Cung Cấp Email Khác:

- **Outlook/Hotmail**: Dùng mật khẩu thông thường với `smtp-mail.outlook.com`
- **Yahoo**: Dùng Mật Khẩu Ứng Dụng từ [account.yahoo.com/security](https://account.yahoo.com/security)
- **Miền tùy chỉnh**: Kiểm tra cài đặt SMTP của nhà cung cấp email

---

## Bước 2: Cấu Hình Tệp `.env`

Chỉnh sửa tệp `.env` của bạn và điền các cài đặt email:

```bash
# Email / Automation (bắt buộc cho --email và automation.py)
SMTP_HOST=smtp.gmail.com           # Gmail: smtp.gmail.com
SMTP_PORT=587                      # Chuẩn: 587 (TLS)
SMTP_USER=your_email@gmail.com     # Địa chỉ email của bạn
SMTP_PASSWORD=your_app_password    # Mật Khẩu Ứng Dụng Gmail (16 ký tự)
SMTP_USE_TLS=true                  # Sử dụng mã hóa TLS
REPORT_EMAIL_FROM=your_email@gmail.com    # Địa chỉ gửi (thường giống SMTP_USER)
REPORT_EMAIL_TO=recipient@example.com     # Người nhận mặc định
AUTO_SEND_REPORT=false             # Đặt thành 'true' để luôn gửi email kết quả
```

### Tham Chiếu Cấu Hình

| Cài Đặt | Ví Dụ | Mô Tả |
|--------|-------|-------|
| `SMTP_HOST` | smtp.gmail.com | Địa chỉ máy chủ SMTP |
| `SMTP_PORT` | 587 | Cổng SMTP (587 cho TLS, 465 cho SSL) |
| `SMTP_USER` | user@gmail.com | Tài khoản email để xác thực |
| `SMTP_PASSWORD` | xxxx xxxx xxxx xxxx | Mật khẩu ứng dụng (không phải mật khẩu thông thường) |
| `SMTP_USE_TLS` | true | Bật mã hóa TLS |
| `REPORT_EMAIL_FROM` | user@gmail.com | Địa chỉ email người gửi |
| `REPORT_EMAIL_TO` | recipient@example.com | Email người nhận mặc định |
| `AUTO_SEND_REPORT` | false | Tự động gửi mỗi lần chạy (true/false) |

---

## Bước 3: Kiểm Tra Cấu Hình Email

Chạy kiểm tra nhanh để xác minh thiết lập của bạn:

```bash
# Kiểm tra với dữ liệu mẫu và email
python automation.py --demo --email

# Đầu ra dự kiến:
# [OK] Job Analysis
# [OK] CV Analysis
# [OK] Interview Prep
# [OK] Cover Letter
# Reports saved:
#   HTML: reports/report_XXXXXX.html
#   JSON: reports/report_XXXXXX.json
#   Duration: X.Xs
#   Email sent to: recipient@example.com
```

---

## Bước 4: Ví Dụ Cách Sử Dụng

### Tùy Chọn A: Gửi Email Theo Yêu Cầu (Được Khuyến Nghị Để Thử Nghiệm)

Chỉ gửi email khi bạn sử dụng cờ `--email`:

```bash
# Demo với email
python automation.py --demo --email

# Với tệp của bạn
python automation.py job_description.pdf resume.pdf --email

# Gửi đến người nhận tùy chỉnh
python automation.py examples/sample_job.txt examples/sample_cv.txt --email-to boss@company.com
```

### Tùy Chọn B: Gửi Email Tự Động (Đặt AUTO_SEND_REPORT=true)

Bật gửi email tự động cho mỗi phân tích:

```bash
# Chỉnh sửa .env
AUTO_SEND_REPORT=true

# Bây giờ mỗi lần chạy sẽ gửi email tự động
python automation.py --demo
python automation.py job_description.pdf resume.pdf

# Bỏ qua email nếu cần
python automation.py --demo --no-email
```

### Tùy Chọn C: Giao Diện Web với Email

```bash
streamlit run app.py
```

Sau đó trong thanh bên, khi email được cấu hình, bạn sẽ thấy một hộp kiểm: "Gửi báo cáo đến email"

---

## Mẫu Email

Email được gửi chứa:

**Chủ đề:** Job Application Analysis Report

**Nội dung:**
- Báo cáo được định dạng HTML chuyên nghiệp
- Bao gồm tất cả các phần phân tích:
  - Tóm tắt Hồ Sơ Công Việc
  - Điểm Khớp CV & Khuyến Nghị
  - Hướng Dẫn Chuẩn Bị Phỏng Vấn
  - Các Biến Thể Thư Xin Việc

**Tệp đính kèm:**
- `report_XXXXXX.html` - Báo cáo HTML được định dạng
- `report_XXXXXX.json` - Dữ liệu JSON thô để xử lý

---

## Khắc Phục Sự Cố

| Lỗi | Nguyên Nhân | Giải Pháp |
|-----|-----------|----------|
| `SMTP authentication failed` | Mật khẩu sai hoặc mật khẩu ứng dụng sai | Sử dụng Mật Khẩu Ứng Dụng Gmail, không phải mật khẩu thông thường |
| `Connection timeout` | Không thể tiếp cận máy chủ SMTP | Kiểm tra giá trị SMTP_HOST và SMTP_PORT |
| `Email not sending` | EMAIL_ENABLED=false | Xác minh tất cả 4 trường bắt buộc được đặt |
| `Connection refused` | Tường lửa chặn cổng 587 | Kiểm tra tường lửa hoặc cài đặt ISP của bạn |
| `Email is not configured` | Thiếu biến env bắt buộc | Điền tất cả 4 trường: SMTP_HOST, SMTP_USER, SMTP_PASSWORD, REPORT_EMAIL_TO |

---

## Các Thực Hành Bảo Mật Tốt Nhất

⚠️ **Không bao giờ cam kết tệp `.env` vào Git**
- Thêm `.env` vào `.gitignore`
- Giữ mật khẩu `.env` riêng tư
- Sử dụng biến môi trường trong sản xuất

✅ **Bảo Mật Gmail:**
- Sử dụng Mật Khẩu Ứng Dụng, không phải mật khẩu chính của bạn
- Giữ Xác Minh Hai Bước được bật
- Thu hồi mật khẩu ứng dụng khi không cần thiết nữa