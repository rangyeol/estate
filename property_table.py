from PySide6.QtWidgets import QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView, QPushButton, QFrame, QCheckBox, QApplication
from PySide6.QtCore import Qt, Signal, Slot
from datetime import datetime
from PySide6.QtGui import QFont, QColor
import re
import copy

class NumericTableWidgetItem(QTableWidgetItem):
    def __init__(self, text, numeric_value):
        super().__init__(text)
        try:
            self.numeric_value = float(numeric_value)
        except (ValueError, TypeError):
            self.numeric_value = float('-inf') 

    def __lt__(self, other):
        if isinstance(other, NumericTableWidgetItem):
            return self.numeric_value < other.numeric_value
        try:
            return self.text() < other.text()
        except AttributeError: 
             return super().__lt__(other)

class PropertyTable(QTableWidget):
    checkbox_toggled = Signal(int, bool)
    detail_button_clicked = Signal(int)

    def __init__(self, parent=None, is_complex_table=False):
        super().__init__(parent)
        self.checked_rows = set()
        self.is_complex_table = is_complex_table
        self._original_header_texts = [] 
        self.average_prices = {}
        self.setup_ui()
        self.cellClicked.connect(self.on_cell_clicked)
        self.cellClicked.connect(self.on_cell_clicked_for_detail)
        if self.horizontalHeader():
            self.horizontalHeader().sortIndicatorChanged.connect(self.update_header_sort_indicators)

        self.field_mapping = {
            'articleNo': '매물번호', 'articleName': '매물명', 'articleStatus': '매물상태',
            'realEstateTypeCode': '부동산유형코드', 'realEstateTypeName': '부동산유형',
            'articleRealEstateTypeCode': '매물부동산유형코드', 'articleRealEstateTypeName': '매물부동산유형',
            'tradeTypeCode': '거래유형코드', 'tradeTypeName': '거래유형',
            'verificationTypeCode': '확인유형코드', 'floorInfo': '층정보',
            'priceChangeState': '가격변동상태', 'isPriceModification': '가격수정여부',
            'dealOrWarrantPrc': '매매/전세가', 'areaName': '면적명', 'area1': '전용면적', 
            'area2': '공급면적', 'direction': '방향', 'articleConfirmYmd': '확인일',
            'articleFeatureDesc': '매물특징', 'tagList': '태그목록',
            'buildingName': '동이름', 'sameAddrCnt': '동일주소매물수', 'sameAddrMaxPrc': '동일주소최고가',
            'sameAddrMinPrc': '동일주소최저가', 'latitude': '위도', 'longitude': '경도',
            'isLocationShow': '위치표시여부', 'realtorName': '부동산중개사명', 'realtorId': '부동산중개사ID',
            'tradeCheckedByOwner': '소유자확인거래', 'isDirectTrade': '직거래여부', 'isInterest': '관심여부',
            'isComplex': '단지여부', 'detailAddress': '상세주소', 'detailAddressYn': '상세주소여부',
            'isVrExposed': 'VR노출여부', 'isSafeLessorOfHug': '안심임대인여부', 'rentPrc': '월세',
            'complexName': '단지명', 'complexNo': '단지번호', 'cortarAddress': '주소'
        }
        self.original_data = []
        self.data = []

    def setup_ui(self):
        header_labels = []
        if self.is_complex_table:
            self.setColumnCount(7); header_labels = ["선택", "단지명", "부동산유형", "면적", "층수", "방향", "정보"]
        else:
            self.setColumnCount(11); header_labels = ["선택", "매물명", "매매/전세가", "월세", "거래유형", "공급/전용면적", "층수", "방향", "확인일", "특징", "상세보기"]
        
        self.setHorizontalHeaderLabels(header_labels)
        self._original_header_texts = list(header_labels)
        self.setAlternatingRowColors(True)
        self.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.setSortingEnabled(True) 
        self.verticalHeader().setVisible(False)
        header = self.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        self.setColumnWidth(0, 40)
        
        if not self.is_complex_table:
            self.setColumnWidth(1, 120); self.setColumnWidth(2, 120); self.setColumnWidth(3, 100);
            self.setColumnWidth(4, 80); self.setColumnWidth(5, 120); self.setColumnWidth(6, 70);
            self.setColumnWidth(7, 90); self.setColumnWidth(8, 90); self.setColumnWidth(9, 200);
            self.setColumnWidth(10, 80)
            header.setSectionResizeMode(9, QHeaderView.ResizeMode.Stretch)
            header.setSectionResizeMode(10, QHeaderView.ResizeMode.Fixed)
        else:
            header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)

        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        self.setStyleSheet(PropertyTable.get_style_sheet())
        
    def load_data(self, data, average_prices=None):
        self.setSortingEnabled(False)
        self.average_prices = average_prices or {}
        self.clearContents(); self.setRowCount(0); self.checked_rows.clear()
        if not data: self.original_data = []; self.data = []; self.setSortingEnabled(True); return
        
        self.original_data = copy.deepcopy(data); self.data = copy.deepcopy(data)
        self.setRowCount(len(data))
        for row, article in enumerate(self.data):
            try:
                checkbox_item = QTableWidgetItem(); checkbox_item.setFlags(Qt.ItemFlag.ItemIsUserCheckable | Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)
                checkbox_item.setCheckState(Qt.CheckState.Unchecked); checkbox_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.setItem(row, 0, checkbox_item)
                if self.is_complex_table: self.fill_complex_row(row, article)
                else:
                    self.fill_article_row(row, article)
                    detail_button = self.create_detail_button(row)
                    if detail_button: self.setCellWidget(row, 10, detail_button)
            except Exception as e: import traceback; traceback.print_exc()
        self.resizeRowsToContents(); self.setSortingEnabled(True)
        self.update_header_sort_indicators(self.horizontalHeader().sortIndicatorSection(), self.horizontalHeader().sortIndicatorOrder())
    
    def _get_area_key(self, article):
        supply_area_str = article.get('area2', '')
        exclusive_area_str = article.get('area1', '')
        def _format_num(num_str):
            if not num_str: return ''
            try: return f"{float(num_str):.2f}".rstrip('0').rstrip('.')
            except (ValueError, TypeError): return str(num_str)
        s_area_fmt = _format_num(supply_area_str)
        e_area_fmt = _format_num(exclusive_area_str)
        if s_area_fmt and e_area_fmt: return f"{s_area_fmt}㎡ ({e_area_fmt}㎡)"
        elif s_area_fmt: return f"{s_area_fmt}㎡"
        elif e_area_fmt: return f"{e_area_fmt}㎡"
        return "-"

    def fill_article_row(self, row, article):
        # (기존 아이템 채우는 로직은 동일)
        # 매물명
        name_item = QTableWidgetItem(article.get('articleName', article.get('complexName', '-')))
        self.setItem(row, 1, name_item)
        # 매매/전세가
        price_str = article.get('dealOrWarrantPrc', '-')
        numeric_price_val = self._get_numeric_value_from_price_str(price_str)
        price_item = NumericTableWidgetItem(self.format_price_in_won(price_str), numeric_price_val)
        price_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self.setItem(row, 2, price_item)
        # 월세
        rent_price_str = article.get('rentPrc', '-')
        numeric_rent_val = self._get_numeric_value_from_rent_str(rent_price_str)
        rent_display = f"{int(numeric_rent_val/10000):,}" if numeric_rent_val > 0 else (rent_price_str or '-')
        rent_item = NumericTableWidgetItem(rent_display, numeric_rent_val)
        rent_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self.setItem(row, 3, rent_item)
        # 거래유형
        trade_type = article.get('tradeTypeName', '-')
        trade_item = QTableWidgetItem(trade_type)
        trade_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setItem(row, 4, trade_item)
        # 면적
        area_key_str = self._get_area_key(article)
        numeric_area_val = float(article.get('area1', 0))
        area_item = NumericTableWidgetItem(area_key_str, numeric_area_val)
        area_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setItem(row, 5, area_item)
        # (이하 층수, 방향 등 나머지 아이템들도 동일하게 채움)
        floor_info_str = article.get('floorInfo', '-'); floor_item = NumericTableWidgetItem(str(floor_info_str), self._parse_floor_info_for_sorting(floor_info_str)); floor_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter); self.setItem(row, 6, floor_item)
        dir_item = QTableWidgetItem(str(article.get('direction', '-'))); dir_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter); self.setItem(row, 7, dir_item)
        confirm_item = QTableWidgetItem(self.format_date(article.get('articleConfirmYmd', '-'))); confirm_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter); self.setItem(row, 8, confirm_item)
        info_item = QTableWidgetItem(str(article.get('articleFeatureDesc', '-'))); info_item.setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter); self.setItem(row, 9, info_item)

        # ▼▼▼ 하이라이트 로직 추가 ▼▼▼
        key = (
            article.get('articleName', article.get('complexName', '')),
            trade_type,
            area_key_str
        )
        avg_price = self.average_prices.get(key)
        
        if avg_price and numeric_price_val > 0 and numeric_price_val < avg_price:
            color = None
            if trade_type == '매매': color = QColor("#FFE4E1") # 선홍색
            elif trade_type == '전세': color = QColor("#E9F5E9") # 연녹색
            elif trade_type == '월세': color = QColor("#E0F7FA") # 하늘색
            
            if color:
                for col in range(self.columnCount()):
                    if self.item(row, col): # 아이템이 있는 경우에만 적용
                        self.item(row, col).setBackground(color)
    
    # ... (이하 기존 메서드들은 변경 없이 유지)
    # _get_numeric_value_from_price_str, format_price_in_won, _get_area_key 등...
    # 이 답변에서는 핵심 수정사항 위주로 보여드렸으므로,
    # 나머지 부분은 이전 답변의 코드를 그대로 사용하시면 됩니다.

    # ... (생략된 기존 코드 시작)
    @Slot(int, Qt.SortOrder)
    def update_header_sort_indicators(self, logical_index, order):
        if not self._original_header_texts or len(self._original_header_texts) != self.columnCount():
            self._original_header_texts = [self.horizontalHeaderItem(i).text().split(" ")[0] if self.horizontalHeaderItem(i) else "" for i in range(self.columnCount())]
        for i in range(self.columnCount()):
            if i < len(self._original_header_texts):
                original_text = self._original_header_texts[i]
                new_text = original_text
                if i == logical_index:
                    if order == Qt.SortOrder.AscendingOrder: new_text = f"{original_text} ▲"
                    elif order == Qt.SortOrder.DescendingOrder: new_text = f"{original_text} ▼"
                header_item = self.horizontalHeaderItem(i)
                if header_item: header_item.setText(new_text)
    

    @staticmethod
    def get_style_sheet():
        return """
            QTableWidget { background-color: white; alternate-background-color: #f5f9fc; border: 1px solid #dce6f1; border-radius: 4px; selection-background-color: #e3f2fd; selection-color: #1976d2; gridline-color: #dce6f1; }
            QTableWidget::item { padding: 4px; border-bottom: 1px solid #e9ecef; }
            QHeaderView::section { background-color: #0077b6; color: white; padding: 6px; border: none; font-weight: bold; text-align: center; }
            QScrollBar:vertical { background: #f8f9fa; width: 10px; border-radius: 5px; margin: 0px; }
            QScrollBar::handle:vertical { background: #ced4da; border-radius: 5px; min-height: 20px; }
            QScrollBar::handle:vertical:hover { background: #adb5bd; }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { border: none; background: none; height: 0px; }
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical { background: none; }
            QTableWidget QTableCornerButton::section { background-color: #0077b6; border: none; }
        """

    def load_data(self, data):
        self.setSortingEnabled(False)
        self.clearContents(); self.setRowCount(0); self.checked_rows.clear()
        if not data: self.original_data = []; self.data = []; self.setSortingEnabled(True); return
        
        header_labels = []
        if self.is_complex_table:
            self.setColumnCount(7); header_labels = ["선택", "단지명", "부동산유형", "면적", "층수", "방향", "정보"]
        else:
            self.setColumnCount(11); header_labels = ["선택", "매물명", "매매/전세가", "월세", "거래유형", "공급/전용면적", "층수", "방향", "확인일", "특징", "상세보기"]
        self.setHorizontalHeaderLabels(header_labels)
        self._original_header_texts = list(header_labels)

        self.original_data = copy.deepcopy(data); self.data = copy.deepcopy(data)
        self.setRowCount(len(data))
        for row, article in enumerate(self.data):
            try:
                checkbox_item = QTableWidgetItem(); checkbox_item.setFlags(Qt.ItemFlag.ItemIsUserCheckable | Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)
                checkbox_item.setCheckState(Qt.CheckState.Unchecked); checkbox_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.setItem(row, 0, checkbox_item)
                if self.is_complex_table: self.fill_complex_row(row, article)
                else:
                    self.fill_article_row(row, article)
                    detail_button = self.create_detail_button(row)
                    if detail_button: self.setCellWidget(row, 10, detail_button)
            except Exception as e: import traceback; traceback.print_exc()
        self.resizeRowsToContents(); self.setSortingEnabled(True)
        self.update_header_sort_indicators(self.horizontalHeader().sortIndicatorSection(), self.horizontalHeader().sortIndicatorOrder())

    def _get_numeric_value_from_price_str(self, price_str):
        if not isinstance(price_str, str) or price_str == '-': return 0 
        try:
            price_str_cleaned = price_str.replace(',', '').strip()
            total_won = 0
            if '억' in price_str_cleaned:
                parts = price_str_cleaned.split('억')
                if parts[0].strip().isdigit(): total_won += int(parts[0].strip()) * 100000000
                if len(parts) > 1 and parts[1].strip().isdigit(): total_won += int(parts[1].strip()) * 10000
            elif price_str_cleaned.isdigit(): total_won += int(price_str_cleaned) * 10000
            return total_won
        except (ValueError, TypeError): return 0

    def _get_numeric_value_from_rent_str(self, rent_str):
        if not rent_str or rent_str == '-' or not rent_str.strip().isdigit(): return 0
        try: return int(rent_str.strip()) * 10000
        except ValueError: return 0
            
    def _parse_floor_info_for_sorting(self, floor_str):
        if not isinstance(floor_str, str): return -1 
        if '/' in floor_str:
            try: return int(floor_str.split('/')[0])
            except ValueError: pass
        if floor_str.endswith('층'):
            try: return int(floor_str[:-1])
            except ValueError: pass
        if floor_str.isdigit():
            try: return int(floor_str)
            except ValueError: pass
        mapping = {"저": 1, "중": 5, "고": 10}
        for k, v in mapping.items():
            if k in floor_str: return v
        return -1

    def fill_article_row(self, row, article):
        name_item = QTableWidgetItem(article.get('articleName', article.get('complexName', '-')))
        name_item.setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        self.setItem(row, 1, name_item)

        price_str = article.get('dealOrWarrantPrc', '-')
        numeric_price_val = self._get_numeric_value_from_price_str(price_str)
        formatted_price_display = self.format_price_in_won(price_str)
        price_item = NumericTableWidgetItem(formatted_price_display, numeric_price_val)
        price_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self.setItem(row, 2, price_item)

        rent_price_str = article.get('rentPrc', article.get('rentPrice', '-'))
        numeric_rent_val = self._get_numeric_value_from_rent_str(rent_price_str)
        formatted_rent_display = "-"
        if numeric_rent_val > 0 : formatted_rent_display = f"{numeric_rent_val:,}"
        elif rent_price_str == '0': formatted_rent_display = "0"
        elif rent_price_str and rent_price_str != '-': formatted_rent_display = rent_price_str
        rent_item = NumericTableWidgetItem(formatted_rent_display, numeric_rent_val)
        rent_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self.setItem(row, 3, rent_item)

        trade_item = QTableWidgetItem(article.get('tradeTypeName', '-'))
        trade_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setItem(row, 4, trade_item)

        # ▼▼▼ 면적 표시 로직 수정 ▼▼▼
        supply_area_str = article.get('area2', '')      # 공급면적
        exclusive_area_str = article.get('area1', '')    # 전용면적

        def _format_num(num_str):
            if not num_str: return ''
            try:
                return f"{float(num_str):.2f}".rstrip('0').rstrip('.')
            except (ValueError, TypeError):
                return str(num_str)

        s_area_fmt = _format_num(supply_area_str)
        e_area_fmt = _format_num(exclusive_area_str)

        formatted_area_display = "-"
        if s_area_fmt and e_area_fmt:
            formatted_area_display = f"{s_area_fmt}㎡ ({e_area_fmt}㎡)"
        elif s_area_fmt:
            formatted_area_display = f"{s_area_fmt}㎡"
        elif e_area_fmt:
            formatted_area_display = f"{e_area_fmt}㎡"
        
        numeric_area_val = 0.0
        try:
            if exclusive_area_str: numeric_area_val = float(exclusive_area_str)
        except ValueError: pass

        area_item = NumericTableWidgetItem(formatted_area_display, numeric_area_val)
        area_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setItem(row, 5, area_item)
        # ▲▲▲ 면적 표시 로직 수정 끝 ▲▲▲

        floor_info_str = article.get('floorInfo', '-')
        numeric_floor_val = self._parse_floor_info_for_sorting(floor_info_str)
        floor_item = NumericTableWidgetItem(str(floor_info_str), numeric_floor_val)
        floor_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setItem(row, 6, floor_item)

        dir_item = QTableWidgetItem(str(article.get('direction', '-')))
        dir_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setItem(row, 7, dir_item)

        confirm_date = self.format_date(article.get('articleConfirmYmd', '-'))
        confirm_item = QTableWidgetItem(confirm_date)
        confirm_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setItem(row, 8, confirm_item)

        info_item = QTableWidgetItem(str(article.get('articleFeatureDesc', '-')))
        info_item.setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        self.setItem(row, 9, info_item)

    def format_price_in_won(self, price_str):
        if not isinstance(price_str, str) or price_str == '-': return "-"
        try:
            price_str_cleaned = price_str.replace(',', '').strip()
            total_won = 0
            if '억' in price_str_cleaned:
                parts = price_str_cleaned.split('억')
                if parts[0].strip().isdigit(): total_won += int(parts[0].strip()) * 100000000
                if len(parts) > 1 and parts[1].strip().isdigit(): total_won += int(parts[1].strip()) * 10000
            elif price_str_cleaned.isdigit(): total_won += int(price_str_cleaned) * 10000
            else: return price_str
            return f"{total_won:,}" if total_won > 0 else (price_str_cleaned if price_str_cleaned == '0' else price_str)
        except (ValueError, TypeError): return price_str
        
    def fill_complex_row(self, row, article):
        complex_name = article.get('complexName', article.get('complexNm', '-'))
        name_item = QTableWidgetItem(complex_name)
        name_item.setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        self.setItem(row, 1, name_item)

        type_name = article.get('realEstateTypeName', article.get('realEstateType', article.get('realEstateTypeNm', '-')))
        if type_name == '-':
            type_code = article.get('realEstateTypeCode', '')
            type_name = self.convert_property_type_code(type_code) if type_code else '-'
        type_item = QTableWidgetItem(type_name)
        type_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setItem(row, 2, type_item)

        area_min_str = article.get('minTotalArea', article.get('minArea', ''))
        area_max_str = article.get('maxTotalArea', article.get('maxArea', ''))
        numeric_area_val = 0.0
        try:
            if area_min_str: numeric_area_val = float(area_min_str)
        except ValueError: pass
        area_info_display = self.format_area_info(area_min_str, area_max_str)
        area_item = NumericTableWidgetItem(area_info_display, numeric_area_val)
        area_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setItem(row, 3, area_item)

        floor_min_str = article.get('lowFloor', article.get('minFloor', ''))
        floor_max_str = article.get('highFloor', article.get('maxFloor', ''))
        numeric_floor_val = self._parse_floor_info_for_sorting(floor_min_str)
        floor_info_display = self.format_floor_info(floor_min_str, floor_max_str)
        floor_item = NumericTableWidgetItem(floor_info_display, numeric_floor_val)
        floor_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setItem(row, 4, floor_item)

        approve_date_str = article.get('useApproveYmd', article.get('approveYmd', ''))
        approve_date_display = self.format_date(approve_date_str)
        direction_item = QTableWidgetItem(approve_date_display) 
        direction_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setItem(row, 5, direction_item)

        household_count_str = article.get('totalHouseholdCount', article.get('householdCount', ''))
        dong_count_str = article.get('totalDongCount', article.get('dongCount', ''))
        numeric_household_val = 0
        info_text_raw = "" # 포맷팅 전 세대수 문자열
        if household_count_str:
            info_text_raw = str(household_count_str)
            try:
                numeric_household_val = int(household_count_str)
            except ValueError: pass # 변환 실패 시 numeric_household_val은 0 유지

        info_text_display = ""
        if household_count_str:
            try:
                info_text_display += f"{int(household_count_str):,}" # 천단위 콤마
            except ValueError:
                info_text_display += household_count_str # 숫자가 아니면 그대로
            info_text_display += "세대"

        if dong_count_str: 
            info_text_display += f" {dong_count_str}동" if info_text_display else f"{dong_count_str}동"
        
        info_item = NumericTableWidgetItem(info_text_display if info_text_display else "-", numeric_household_val)
        info_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setItem(row, 6, info_item)

    def format_area_info(self, area_min, area_max):
        if area_min and area_max and area_min != area_max:
            try:
                area_min_fmt = f"{float(area_min):.1f}".rstrip('0').rstrip('.') if '.' in f"{float(area_min):.1f}" else f"{float(area_min):.0f}"
                area_max_fmt = f"{float(area_max):.1f}".rstrip('0').rstrip('.') if '.' in f"{float(area_max):.1f}" else f"{float(area_max):.0f}"
                return f"{area_min_fmt}~{area_max_fmt}㎡"
            except (ValueError, TypeError): return f"{area_min}~{area_max}㎡"
        elif area_min:
            try:
                area_min_fmt = f"{float(area_min):.1f}".rstrip('0').rstrip('.') if '.' in f"{float(area_min):.1f}" else f"{float(area_min):.0f}"
                return f"{area_min_fmt}㎡"
            except (ValueError, TypeError): return f"{area_min}㎡"
        return "-"

    def format_article_area(self, area_value, area_name):
        if not area_value: return "-"
        try:
            area_fmt = f"{float(area_value):.1f}".rstrip('0').rstrip('.') if '.' in f"{float(area_value):.1f}" else f"{float(area_value):.0f}"
            return f"{area_fmt}㎡({area_name})" if area_name else f"{area_fmt}㎡"
        except (ValueError, TypeError):
            return f"{area_value}㎡({area_name})" if area_name else f"{area_value}㎡"

    def format_floor_info(self, floor_min, floor_max):
        if floor_min and floor_max and floor_min != floor_max: return f"{floor_min}~{floor_max}층"
        elif floor_min: return f"{floor_min}층" if isinstance(floor_min, str) and floor_min.isdigit() else f"{floor_min}"
        return "-"

    def format_date(self, date_str):
        if not date_str or date_str == '-': return "-"
        date_str = str(date_str)
        if len(date_str) == 8: return f"{date_str[:4]}.{date_str[4:6]}.{date_str[6:]}"
        elif len(date_str) == 6: return f"{date_str[:4]}.{date_str[4:6]}"
        return date_str

    def verify_detail_buttons(self):
        missing_buttons = [row for row in range(self.rowCount()) if not self.cellWidget(row, 10) or not isinstance(self.cellWidget(row, 10), QPushButton)]
        if missing_buttons:
            print(f"경고: 다음 행에 상세보기 버튼이 없습니다: {missing_buttons}")
            for row in missing_buttons:
                try:
                    detail_button = self.create_detail_button(row)
                    if detail_button: self.setCellWidget(row, 10, detail_button); print(f"행 {row}: 상세보기 버튼 생성 성공")
                except Exception as e: print(f"행 {row}: 상세보기 버튼 생성 실패 - {e}")
        else: print("모든 행에 상세보기 버튼이 정상적으로 설정되었습니다.")

    def create_detail_button(self, row):
        if not self.is_complex_table:
            if not hasattr(self, 'original_data') or not self.original_data or not (0 <= row < len(self.original_data)):
                print(f"create_detail_button: 행 {row} 데이터 접근 불가")
                return None
            button = QPushButton("상세보기")
            button.setStyleSheet(PropertyTable.get_detail_button_style_sheet())
            button.setProperty("row", row)
            try: button.clicked.disconnect()
            except: pass
            button.clicked.connect(lambda checked=False, r=row: self.on_detail_button_clicked(r))
            return button
        return None

    @staticmethod
    def get_detail_button_style_sheet():
        return """
            QPushButton { background-color: #0077b6; color: white; border: none; border-radius: 4px; padding: 4px 8px; font-weight: bold; font-size: 9pt; }
            QPushButton:hover { background-color: #00b4d8; } 
            QPushButton:pressed { background-color: #005f8f; }
        """

    def on_detail_button_clicked(self, row):
        print(f"\n===== on_detail_button_clicked: 행 {row} 상세보기 버튼 클릭 시작 =====")
        sender = self.sender()
        if sender and isinstance(sender, QPushButton):
            stored_row = sender.property("row")
            if stored_row is not None and isinstance(stored_row, (int, float)) and stored_row != row:
                print(f"버튼에 저장된 행 번호({stored_row})로 업데이트 (기존: {row})")
                row = int(stored_row)
        if not hasattr(self, 'original_data') or not self.original_data: print("데이터가 없습니다."); return
        if not (0 <= row < len(self.original_data)):
            print(f"유효하지 않은 행 번호: {row} (범위: 0-{len(self.original_data)-1})")
            row = max(0, min(row, len(self.original_data) - 1))
            print(f"행 번호가 {row}로 보정되었습니다.")
        try:
            print(f"detail_button_clicked 시그널 발생: 행 {row}")
            self.detail_button_clicked.emit(row)
        except Exception as e: print(f"시그널 발생 중 오류: {str(e)}")
        print(f"===== on_detail_button_clicked: 행 {row} 상세보기 버튼 클릭 종료 =====\n")

    def on_cell_clicked(self, row, column):
        try:
            if not hasattr(self, 'data') or not self.data: return
            if not (0 <= row < self.rowCount() and 0 <= column < self.columnCount()): return
            if not self.is_complex_table and column == self.columnCount() - 1: return
            item = self.item(row, 0)
            if not item:
                item = QTableWidgetItem()
                item.setFlags(Qt.ItemFlag.ItemIsUserCheckable | Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.setItem(row, 0, item)
            new_state = Qt.CheckState.Unchecked if item.checkState() == Qt.CheckState.Checked else Qt.CheckState.Checked
            item.setCheckState(new_state)
            is_checked = (new_state == Qt.CheckState.Checked)
            if is_checked: self.checked_rows.add(row)
            else: self.checked_rows.discard(row)
            self.checkbox_toggled.emit(row, is_checked)
            QApplication.processEvents()
        except Exception as e: import traceback; traceback.print_exc()

    def on_cell_clicked_for_detail(self, row, column):
        try:
            if not self.is_complex_table and column == self.columnCount() - 1:
                widget = self.cellWidget(row, column)
                if widget and isinstance(widget, QPushButton): widget.click()
                else: self.on_detail_button_clicked(row)
        except Exception as e: import traceback; traceback.print_exc()

    def get_checked_items(self): return sorted(list(self.checked_rows))
    def get_checked_data(self):
        if not hasattr(self, 'data') or not self.data: return []
        return [self.data[row] for row in self.get_checked_items() if 0 <= row < len(self.data)]
    def get_checked_rows(self): return list(self.checked_rows)

    def check_all_items(self, checked=True):
        check_state = Qt.CheckState.Checked if checked else Qt.CheckState.Unchecked
        for row in range(self.rowCount()):
            item = self.item(row, 0)
            if item and item.checkState() != check_state:
                item.setCheckState(check_state)
                if checked: self.checked_rows.add(row)
                else: self.checked_rows.discard(row)
                self.checkbox_toggled.emit(row, checked)
        if self.rowCount() > 0: self.checkbox_toggled.emit(self.rowCount() - 1, checked)

    def convert_property_type_code(self, code):
        type_mapping = {'APT': '아파트', 'OPST': '오피스텔', 'VL': '빌라', 'DDDGG': '단독/다가구', 'OR': '원룸', 'JWJT': '주택/점포', 'APTHGFC': '아파트형공장', 'SGJT': '상가주택', 'TOJI': '토지', 'JSGJ': '재개발/재건축', 'GM': '공장/창고', 'SANG': '상가', 'SJ': '사무실', 'OFC': '오피스'}
        return type_mapping.get(code, code)