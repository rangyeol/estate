from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QGridLayout, QGroupBox, QScrollArea, QPushButton,
    QFileDialog, QMessageBox, QFrame
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
import json

class PropertyDetailWidget(QWidget):
    """매물 상세 정보 표시 위젯 (모든 정보 표시, 별도 창으로)"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_data = None
        
        self.setWindowFlags(Qt.Window) 
        
        self.init_ui()
        self.init_mappings()
        self.apply_modern_style()

    def init_ui(self):
        """UI 초기화"""
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(15)

        title_layout = QHBoxLayout()
        self.title_label = QLabel("부동산 상세 정보") 
        self.title_label.setObjectName("title_label")
        title_layout.addWidget(self.title_label)
        title_layout.addStretch()

        self.export_button = QPushButton("JSON 내보내기")
        self.export_button.clicked.connect(self.export_to_json)
        self.export_button.setEnabled(False)
        title_layout.addWidget(self.export_button)
        main_layout.addLayout(title_layout)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        main_layout.addWidget(self.scroll_area)

        initial_content_widget = QWidget()
        self.scroll_area.setWidget(initial_content_widget)
        initial_layout = QVBoxLayout(initial_content_widget)
        self.status_label_initial = QLabel("표시할 매물을 선택하세요.")
        self.status_label_initial.setAlignment(Qt.AlignmentFlag.AlignCenter)
        initial_layout.addWidget(self.status_label_initial)

        self.resize(550, 750)

    def _add_info_entry(self, layout, row, label_text, value):
        """Grid 레이아웃에 정보 항목(라벨, 값)을 추가하는 헬퍼 함수"""
        if value is None or value == '' or (isinstance(value, list) and not value):
            # 값이 없거나 빈 리스트면 '-'로 표시하거나, 아예 항목을 추가하지 않을 수 있습니다.
            # 여기서는 명시적으로 '-'를 표시하도록 수정 가능 (선택사항)
            # 또는, 현재처럼 그냥 반환하여 아무것도 추가 안 함.
            return 

        if isinstance(value, list):
            display_value = ', '.join(map(str, value))
        elif isinstance(value, bool):
            display_value = "예" if value else "아니오"
        else:
            display_value = str(value)

        label = QLabel(label_text)
        label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignTop)
        label.setStyleSheet("font-weight: bold; color: #566573; padding-top: 4px;")
        
        value_label = QLabel(display_value)
        value_label.setWordWrap(True)
        value_label.setTextInteractionFlags(Qt.TextInteractionFlags.TextSelectableByMouse)
        
        layout.addWidget(label, row, 0)
        layout.addWidget(value_label, row, 1)

    def update_property_details(self, data):
        """매물 상세 정보를 UI에 업데이트합니다."""
        if not isinstance(data, dict):
            if hasattr(self, 'status_label_initial'):
                self.status_label_initial.hide()
            
            error_content_widget = QWidget()
            self.scroll_area.setWidget(error_content_widget)
            error_layout = QVBoxLayout(error_content_widget)
            error_label = QLabel("데이터 형식이 올바르지 않습니다.")
            error_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            error_layout.addWidget(error_label)
            return

        self.current_data = data
        self.export_button.setEnabled(True)
        
        self.setWindowTitle(f"매물 상세 정보 - {data.get('articleName', data.get('complexName', ''))}") 
        self.title_label.setText(f"{data.get('articleName', data.get('complexName', '부동산 상세 정보'))}")

        new_content_widget = QWidget()
        self.scroll_area.setWidget(new_content_widget)
        content_layout = QVBoxLayout(new_content_widget)
        content_layout.setSpacing(12)
        content_layout.setContentsMargins(10, 5, 10, 15)
        
        displayed_fields = set()
        
        basic_group = QGroupBox("기본 정보")
        basic_layout = QGridLayout(basic_group)
        basic_layout.setColumnStretch(1, 1)
        
        def add_basic(key, label):
            self._add_info_entry(basic_layout, basic_layout.rowCount(), label, data.get(key))
            displayed_fields.add(key)
        
        add_basic('articleName', '매물명:')
        add_basic('complexName', '단지명:')
        add_basic('cortarAddress', '주소:')
        add_basic('articleNo', '매물번호:')
        add_basic('realEstateTypeName', '부동산 유형:')
        self._add_info_entry(basic_layout, basic_layout.rowCount(), "매물 상태:", self.get_mapped_value('articleStatus', data.get('articleStatus')))
        displayed_fields.add('articleStatus')
        self._add_info_entry(basic_layout, basic_layout.rowCount(), "매물 확인일:", self.format_date(data.get('articleConfirmYmd')))
        displayed_fields.add('articleConfirmYmd')
        content_layout.addWidget(basic_group)
        
        price_group = QGroupBox("가격 및 거래 정보")
        price_layout = QGridLayout(price_group)
        price_layout.setColumnStretch(1, 1)
        deal_price = self.format_price(data.get('dealOrWarrantPrc', ''))
        self._add_info_entry(price_layout, price_layout.rowCount(), "매매/전세가:", f"{deal_price} 원" if deal_price != '-' else '-')
        displayed_fields.add('dealOrWarrantPrc')
        
        # --- 월세 표시 수정된 로직 ---
        rent_price_str = data.get('rentPrc') # 원본 월세값 (문자열 예상)
        
        if rent_price_str: # 값이 None이나 빈 문자열이 아닌 경우
            if rent_price_str == '-':
                self._add_info_entry(price_layout, price_layout.rowCount(), "월세:", "-")
            elif rent_price_str == '0':
                self._add_info_entry(price_layout, price_layout.rowCount(), "월세:", "0 원")
            else:
                try:
                    # 문자열을 정수로 변환 시도 (만원 단위로 가정)
                    rent_amount_man_won = int(rent_price_str)
                    # 원 단위로 변환
                    rent_amount_won = rent_amount_man_won * 10000
                    # 포맷팅하여 표시
                    self._add_info_entry(price_layout, price_layout.rowCount(), "월세:", f"{rent_amount_won:,} 원")
                except ValueError:
                    # 정수 변환 실패 시 (예: "삼십만원" 같은 텍스트), 원본 값과 함께 안내 문구 표시
                    self._add_info_entry(price_layout, price_layout.rowCount(), "월세:", f"{rent_price_str} (금액 직접 확인)")
        # rent_price_str가 None이거나 빈 문자열이면 아무것도 표시하지 않음 (또는 '-' 표시 원하면 추가)
        # else:
        #     self._add_info_entry(price_layout, price_layout.rowCount(), "월세:", "-")
        # --- 월세 표시 수정 끝 ---
        displayed_fields.add('rentPrc')

        self._add_info_entry(price_layout, price_layout.rowCount(), "거래 유형:", data.get('tradeTypeName'))
        displayed_fields.add('tradeTypeName')
        content_layout.addWidget(price_group)
        
        area_group = QGroupBox("면적 및 구조")
        area_layout = QGridLayout(area_group)
        area_layout.setColumnStretch(1, 1)
        area_supply = data.get('area2', '-') 
        area_exclusive = data.get('area1', '-')
        area_str = f"{area_supply}㎡ / {area_exclusive}㎡"
        self._add_info_entry(area_layout, area_layout.rowCount(), "공급/전용면적:", area_str)
        displayed_fields.update(['area1', 'area2'])
        self._add_info_entry(area_layout, area_layout.rowCount(), "층 정보:", data.get('floorInfo'))
        displayed_fields.add('floorInfo')
        self._add_info_entry(area_layout, area_layout.rowCount(), "방향:", data.get('direction'))
        displayed_fields.add('direction')
        self._add_info_entry(area_layout, area_layout.rowCount(), "동 이름:", data.get('buildingName'))
        displayed_fields.add('buildingName')
        content_layout.addWidget(area_group)

        complex_info_group = QGroupBox("단지 추가 정보")
        complex_info_layout = QGridLayout(complex_info_group)
        complex_info_layout.setColumnStretch(1, 1)
        
        def add_complex_info(key, label):
            value = data.get(key)
            if value not in [None, '', 0, '0']: 
                 self._add_info_entry(complex_info_layout, complex_info_layout.rowCount(), label, value)
                 displayed_fields.add(key)

        add_complex_info('totalHouseholdCount', '총 세대수:')
        add_complex_info('totalDongCount', '총 동수:')
        self._add_info_entry(complex_info_layout, complex_info_layout.rowCount(), "사용승인일:", self.format_date(data.get('useApproveYmd'))) # format_date 적용
        displayed_fields.add('useApproveYmd')
        add_complex_info('lowFloor', '최저층:')
        add_complex_info('highFloor', '최고층:')
        
        if complex_info_layout.rowCount() > 0: 
            content_layout.addWidget(complex_info_group)

        all_details_group = QGroupBox("기타 상세 정보")
        all_details_layout = QGridLayout(all_details_group)
        all_details_layout.setColumnStretch(1, 1)
        
        for key, value in sorted(data.items()):
            if key not in displayed_fields:
                label = self.field_mapping.get(key, key.replace('_', ' ').title()) 
                mapped_value = self.get_mapped_value(key, value)
                self._add_info_entry(all_details_layout, all_details_layout.rowCount(), f"{label}:", mapped_value)
        
        if all_details_layout.rowCount() > 0:
            content_layout.addWidget(all_details_group)

        content_layout.addStretch()

    def format_price(self, price_str):
        if not isinstance(price_str, str) or price_str == '-':
            return "-"
        try:
            price_str_cleaned = price_str.replace(',', '').strip()
            total_won = 0
            if '억' in price_str_cleaned:
                parts = price_str_cleaned.split('억')
                if parts[0].strip().isdigit():
                    total_won += int(parts[0].strip()) * 100000000
                if len(parts) > 1 and parts[1].strip().isdigit():
                    total_won += int(parts[1].strip()) * 10000
                elif len(parts) > 1 and not parts[1].strip(): # "X억" 형태
                     pass # 이미 억 단위는 처리됨
                elif not parts[0].strip().isdigit() and len(parts) > 1 and not parts[1].strip(): # "억"만 있는 경우 등
                    return price_str # 원래 문자열 반환
            elif price_str_cleaned.isdigit():
                total_won += int(price_str_cleaned) * 10000
            else:
                return price_str 
            return f"{total_won:,}" if total_won > 0 else price_str_cleaned if price_str_cleaned == '0' else price_str
        except (ValueError, TypeError):
            return price_str

    def format_date(self, date_str):
        if not date_str or not isinstance(date_str, str) or len(date_str) < 6 : # YYYYMM 또는 YYYYMMDD
            return date_str
        try:
            if len(date_str) == 8 : # YYYYMMDD
                 return f"{date_str[:4]}.{date_str[4:6]}.{date_str[6:]}"
            elif len(date_str) == 6 : # YYYYMM
                 return f"{date_str[:4]}.{date_str[4:6]}"
            return date_str # 그 외 형식
        except:
            return date_str

    def get_mapped_value(self, field_key, code):
        if code is None: return None 
        if isinstance(code, bool):
            bool_str_val = str(code).lower()
            if field_key in self.code_value_mapping and bool_str_val in self.code_value_mapping[field_key]:
                 return self.code_value_mapping[field_key][bool_str_val]
            return "예" if code else "아니오" 
        if isinstance(code, str):
            return self.code_value_mapping.get(field_key, {}).get(code, code)
        return str(code)

    def export_to_json(self):
        if not self.current_data:
            QMessageBox.warning(self, "내보내기 오류", "내보낼 데이터가 없습니다.")
            return
        
        default_filename = f"{self.current_data.get('articleNo', 'property_detail')}.json"
        file_path, _ = QFileDialog.getSaveFileName(
            self, "JSON 파일 저장", default_filename, "JSON 파일 (*.json)"
        )
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(self.current_data, f, ensure_ascii=False, indent=2)
                QMessageBox.information(self, "내보내기 성공", f"데이터가 성공적으로 저장되었습니다:\n{file_path}")
            except Exception as e:
                QMessageBox.critical(self, "내보내기 오류", f"파일 저장 중 오류가 발생했습니다:\n{str(e)}")
    
    def apply_modern_style(self):
        primary_color = "#0077b6"
        text_color = "#2c3e50"
        background_color = "#f5f7fa" 
        card_color = "#ffffff"       
        border_color = "#dfe6e9"
        self.setStyleSheet(f"""
            PropertyDetailWidget {{ background-color: {background_color}; }}
            #title_label {{
                font-weight: bold;
                font-size: 16pt;
                color: {primary_color};
                padding: 5px 0 10px 0; 
            }}
            QGroupBox {{
                font-weight: bold;
                font-size: 11pt;
                border: 1px solid {border_color};
                border-radius: 8px;
                margin-top: 1em; 
                background-color: {card_color};
                padding: 10px; 
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 0 10px;
                margin-left: 10px;
                color: {primary_color};
            }}
            QLabel {{
                font-size: 10pt;
                color: {text_color};
                padding: 3px; 
            }}
            QScrollArea {{
                background-color: transparent;
                border: none; 
            }}
        """)

    def init_mappings(self):
        """필드 및 코드 매핑 정보 전체 초기화 (기존 사용자 제공 내용 기반)"""
        self.field_mapping = {
            'articleNo': '매물번호', 'articleName': '매물명', 'articleStatus': '매물상태',
            'realEstateTypeCode': '부동산유형코드', 'realEstateTypeName': '부동산유형',
            'articleRealEstateTypeCode': '매물부동산유형코드', 'articleRealEstateTypeName': '매물부동산유형',
            'tradeTypeCode': '거래유형코드', 'tradeTypeName': '거래유형',
            'verificationTypeCode': '확인유형코드', 'floorInfo': '층정보',
            'priceChangeState': '가격변동상태', 'isPriceModification': '가격수정여부',
            'dealOrWarrantPrc': '매매/전세가', 'areaName': '면적명',
            'area1': '전용면적(㎡)', 'area2': '공급면적(㎡)', 'direction': '방향',
            'articleConfirmYmd': '매물확인일', 'siteImageCount': '이미지수',
            'articleFeatureDesc': '매물특징', 'tagList': '태그목록',
            'buildingName': '동이름', 'sameAddrCnt': '동일주소매물수',
            'sameAddrDirectCnt': '동일주소직거래수', 'sameAddrMaxPrc': '동일주소최고가',
            'sameAddrMinPrc': '동일주소최저가', 'cpid': '제휴사ID',
            'cpName': '제휴사명', 'cpPcArticleUrl': 'PC매물URL',
            'cpPcArticleBridgeUrl': '제휴사PC매물연결URL',
            'cpPcArticleLinkUseAtArticleTitleYn': 'PC매물제목링크사용여부',
            'cpPcArticleLinkUseAtCpNameYn': 'PC제휴사명링크사용여부',
            'cpMobileArticleUrl': '모바일매물URL',
            'cpMobileArticleLinkUseAtArticleTitleYn': '모바일매물제목링크사용여부',
            'cpMobileArticleLinkUseAtCpNameYn': '모바일제휴사명링크사용여부',
            'latitude': '위도', 'longitude': '경도',
            'isLocationShow': '위치표시여부', 'realtorName': '부동산중개사명',
            'realtorId': '부동산중개사ID', 'tradeCheckedByOwner': '소유자확인거래',
            'isDirectTrade': '직거래여부', 'isInterest': '관심여부',
            'isComplex': '단지여부', 'detailAddress': '상세주소',
            'detailAddressYn': '상세주소여부', 'isVrExposed': 'VR노출여부',
            'isSafeLessorOfHug': '안심임대인여부', 'representativeImgUrl': '대표이미지URL',
            'representativeImgTypeCode': '대표이미지유형코드',
            'representativeImgThumb': '대표이미지썸네일',
            'rentPrc': '월세(만원)', 'complexName': '단지명', 'complexNo': '단지번호',
            'cortarAddress': '주소', 'cortarNo': '지역코드', 'deepLink': '링크',
            'highFloor': '최고층', 'lowFloor': '최저층',
            'maxSupplyArea': '최대공급면적', 'maxTotalArea': '최대전체면적',
            'minSupplyArea': '최소공급면적', 'minTotalArea': '최소전체면적',
            'totalDongCount': '총동수', 'totalHouseholdCount': '총세대수',
            'useApproveYmd': '사용승인일', 'useYn': '사용여부'
        }
        
        self.code_value_mapping = {
            'articleStatus': {'R': '정상', 'C': '완료', 'D': '삭제', 'W': '대기', 'I': '처리중'},
            'realEstateTypeCode': {'APT': '아파트', 'OPST': '오피스텔', 'ABYG': '아파트분양권', 'OBYG': '오피스텔분양권', 'JGC': '재건축', 'HOUSE': '단독/다가구', 'DDDGG': '단독/다가구', 'LAND': '토지', 'RHTLR': '연립/다세대', 'QTBNR': '상가주택', 'HSTAY': '홈스테이', 'BDC': '건물', 'OPRM': '원룸', 'STORE': '상가', 'OFFICE': '사무실', 'LFARM': '전원주택', 'FACT': '공장/창고'},
            'articleRealEstateTypeCode': {'APT': '아파트', 'OPST': '오피스텔', 'ABYG': '아파트분양권', 'OBYG': '오피스텔분양권', 'JGC': '재건축', 'HOUSE': '단독/다가구', 'DDDGG': '단독/다가구', 'LAND': '토지', 'RHTLR': '연립/다세대', 'QTBNR': '상가주택', 'HSTAY': '홈스테이', 'BDC': '건물', 'OPRM': '원룸', 'STORE': '상가', 'OFFICE': '사무실', 'LFARM': '전원주택', 'FACT': '공장/창고'},
            'tradeTypeCode': {'A1': '매매', 'B1': '전세', 'B2': '월세', 'B3': '단기임대', 'C1': '입주권매매', 'C2': '입주권전세', 'D1': '매매완료', 'E1': '계약해지', 'F1': '보류'},
            'verificationTypeCode': {'OWNER': '소유자확인', 'CERT': '인증매물', 'CONFIRM': '확인매물', 'DIRECT': '직거래', 'AGENCY': '중개사', 'NONE': '미확인'},
            'priceChangeState': {'SAME': '동일', 'UP': '상승', 'DOWN': '하락', 'NEW': '신규'},
            'isPriceModification': {'true': '수정됨', 'false': '수정안됨', True: '수정됨', False: '수정안됨'},
            'cpPcArticleLinkUseAtArticleTitleYn': {'Y': '사용함', 'N': '사용안함', 'true': '사용함', 'false': '사용안함', True: '사용함', False: '사용안함'},
            'cpPcArticleLinkUseAtCpNameYn': {'Y': '사용함', 'N': '사용안함', 'true': '사용함', 'false': '사용안함', True: '사용함', False: '사용안함'},
            'cpMobileArticleLinkUseAtArticleTitleYn': {'Y': '사용함', 'N': '사용안함', 'true': '사용함', 'false': '사용안함', True: '사용함', False: '사용안함'},
            'cpMobileArticleLinkUseAtCpNameYn': {'Y': '사용함', 'N': '사용안함', 'true': '사용함', 'false': '사용안함', True: '사용함', False: '사용안함'},
            'isLocationShow': {'Y': '표시함', 'N': '표시안함', 'true': '표시함', 'false': '표시안함', True: '표시함', False: '표시안함'},
            'tradeCheckedByOwner': {'Y': '확인됨', 'N': '확인안됨', 'true': '확인됨', 'false': '확인안됨', True: '확인됨', False: '확인안됨'},
            'isDirectTrade': {'Y': '직거래', 'N': '중개거래', 'true': '직거래', 'false': '중개거래', True: '직거래', False: '중개거래'},
            'isInterest': {'Y': '관심매물', 'N': '일반매물', 'true': '관심매물', 'false': '일반매물', True: '관심매물', False: '일반매물'},
            'isComplex': {'Y': '단지', 'N': '일반매물', 'true': '단지', 'false': '일반매물', True: '단지', False: '일반매물'},
            'detailAddressYn': {'Y': '표시함', 'N': '표시안함', 'true': '표시함', 'false': '표시안함', True: '표시함', False: '표시안함'},
            'isVrExposed': {'Y': 'VR있음', 'N': 'VR없음', 'true': 'VR있음', 'false': 'VR없음', True: 'VR있음', False: 'VR없음'},
            'isSafeLessorOfHug': {'Y': '안심임대인', 'N': '일반임대인', 'true': '안심임대인', 'false': '일반임대인', True: '안심임대인', False: '일반임대인'}
        }