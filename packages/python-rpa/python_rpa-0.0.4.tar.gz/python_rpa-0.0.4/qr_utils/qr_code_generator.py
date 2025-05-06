import qrcode


def generate_qr_code(url, output_file_name="qrcode.png"):
  qr = qrcode.QRCode(
      version=1,  # QR 코드 버전 (1~40)
      error_correction=qrcode.constants.ERROR_CORRECT_L,  # 오류 수정 레벨
      box_size=10,  # QR 코드 박스 크기
      border=4,  # 테두리 크기
  )
  
  qr.add_data(url)
  qr.make(fit=True)

  img = qr.make_image(fill_color="black", back_color="white")
  img.save(output_file_name)
  
  return output_file_name
