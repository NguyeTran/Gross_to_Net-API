from fastapi import FastAPI, File, UploadFile, Form
from fastapi.responses import JSONResponse, StreamingResponse
import pandas as pd
from io import BytesIO
from calculator import calculate_gross_to_net # Import hàm đã sửa

app = FastAPI(title="Gross to Net Salary API")

# --- Endpoint 1: Tính toán cho một người ---
@app.post("/calculate_single", summary="Tính Lương Gross -> Net cho một người")
def calculate_single(
    gross_salary: float = Form(..., description="Tổng thu nhập Gross (Lương + Thưởng)"), 
    insurance_base: float = Form(..., description="Mức lương cơ bản dùng để đóng BHXH, BHYT, BHTN"), 
    num_dependents: int = Form(0, description="Số người phụ thuộc"), 
    tax_method: str = Form('hien_hanh', description="Phương pháp tính thuế: 'hien_hanh' (7 bậc/11tr), '2026' (5 bậc/15.5tr), hoặc 'toan_phan' (10% vãng lai)")
):
    """
    Tính lương Net từ Tổng thu nhập (Gross) và Mức lương đóng BH theo các phương pháp tính thuế khác nhau.
    """
    if gross_salary < 0 or num_dependents < 0 or insurance_base < 0:
        return JSONResponse(status_code=400, content={"message": "Dữ liệu đầu vào không hợp lệ."})

    # Đảm bảo tax_method là hợp lệ (tùy thuộc vào logic xử lý trong calculator.py)
    if tax_method not in ['hien_hanh', '2026', 'toan_phan']:
        return JSONResponse(status_code=400, content={"message": "Tax_Method không hợp lệ."})

    result = calculate_gross_to_net(gross_salary, insurance_base, num_dependents, tax_method)
    return result

# --- Endpoint 2: Tính toán hàng loạt qua file Excel ---
@app.post("/calculate_batch", summary="Tính Lương Gross -> Net hàng loạt bằng file Excel (.xlsx)")
async def calculate_batch(file: UploadFile = File(..., description="File Excel chứa dữ liệu nhân viên")):
    """
    Tải lên file Excel (.xlsx). File phải có các cột sau:
    - Gross_Salary (float): Tổng thu nhập Gross
    - Insurance_Base (float): Mức lương cơ bản đóng BHXH
    - Num_Dependents (int): Số người phụ thuộc
    - Tax_Method (str): Phương pháp tính thuế ('hien_hanh', '2026', 'toan_phan')
    """
    if file.filename.split('.')[-1] not in ('xlsx', 'xls'):
        return JSONResponse(status_code=400, content={"message": "Chỉ chấp nhận file định dạng .xlsx hoặc .xls."})

    try:
        # Đọc nội dung file
        content = await file.read()
        df = pd.read_excel(BytesIO(content))
        
        # Kiểm tra các cột bắt buộc
        required_cols = ['Gross_Salary', 'Insurance_Base', 'Num_Dependents', 'Tax_Method']
        if not all(col in df.columns for col in required_cols):
            return JSONResponse(status_code=400, content={
                "message": "File Excel thiếu một hoặc nhiều cột bắt buộc.",
                "required_columns": required_cols
            })

        results = []
        
        # Áp dụng hàm tính toán cho từng hàng
        # Dùng .apply() cho hiệu suất tốt hơn so với vòng lặp truyền thống
        def process_row(row):
            try:
                # Chuyển đổi dữ liệu và gọi hàm tính toán
                gross = float(row['Gross_Salary'])
                insurance_base = float(row['Insurance_Base'])
                dependents = int(row['Num_Dependents'])
                tax_method = str(row['Tax_Method']).lower() # Đảm bảo chữ thường

                # Kiểm tra giá trị hợp lệ trước khi tính
                if gross < 0 or insurance_base < 0 or dependents < 0:
                     return {"Error": "Dữ liệu đầu vào âm."}

                if tax_method not in ['hien_hanh', '2026', 'toan_phan']:
                    return {"Error": f"Tax_Method '{tax_method}' không hợp lệ."}
                
                return calculate_gross_to_net(gross, insurance_base, dependents, tax_method)

            except Exception as e:
                # Xử lý lỗi trong quá trình chuyển đổi hoặc tính toán của 1 dòng
                return {"Error": f"Lỗi xử lý dữ liệu: {str(e)}"}

        # Áp dụng hàm xử lý lên DataFrame
        df_results = df.apply(process_row, axis=1, result_type='expand')
        
        # Ghép kết quả vào DataFrame gốc (Tùy chọn, để dễ so sánh)
        final_df = pd.concat([df, df_results], axis=1)

        # Chuẩn bị file Excel đầu ra
        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            final_df.to_excel(writer, index=False, sheet_name='GrossToNet_Results')
        output.seek(0)
        
        # Trả về file Excel cho người dùng tải về
        return StreamingResponse(
            output,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": "attachment; filename=GrossToNet_Results.xlsx"}
        )

    except Exception as e:
        return JSONResponse(status_code=500, content={"message": f"Lỗi server trong quá trình xử lý: {str(e)}"})