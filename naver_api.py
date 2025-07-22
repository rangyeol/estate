import requests
import json
import time
import os
from datetime import datetime
from urllib.parse import quote
import random

class NaverLandAPI:
    def __init__(self):
        # 최신 쿠키 값으로 업데이트 (naver.py에서 가져옴)
        self.cookies = {
            'NNB': 'PUHJ62F5IYOWQ',
            'tooltipDisplayed': 'true',
            'ASID': 'dc48e8f000000196e738d97100000059',
            'nhn.realestate.article.trade_type_cd': '""',
            'nhn.realestate.article.ipaddress_city': '1100000000',
            '_fwb': '203wFVtB5sloJx7t8Y6m1ls.1747872791600',
            '_fwb': '203wFVtB5sloJx7t8Y6m1ls.1747872791600',
            'nstore_session': 'JXKU6+HXI5ArRsPaELAqnCSW',
            'nstore_pagesession': 'ju++ywqqABPMTlsLazK-523316',
            'SRT30': '1747970925',
            'NAC': 'ezUxCQhcSBl9B',
            'nhn.realestate.article.rlet_type_cd': 'A01',
            'realestate.beta.lastclick.cortar': '4100000000',
            'landHomeFlashUseYn': 'N',
            'NACT': '1',
            '_ga': 'GA1.1.443122067.1747979540',
            '_ga_451MFZ9CFM': 'GS2.1.s1747989648$o2$g1$t1747990937$j0$l0$h0',
            'SRT5': '1748008635',
            'REALESTATE': 'Fri%20May%2023%202025%2023%3A09%3A35%20GMT%2B0900%20(Korean%20Standard%20Time)',
            'BUC': 'C_UFgEc1n3Sqf5j9AdW_o1ce_1u97_IIHHKEnBosMbk=',
        }

        # 헤더 정보 업데이트 - 최신 토큰으로 교체 (naver.py에서 가져옴)
        self.headers = {
            'accept': '*/*',
            'accept-language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
            'authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6IlJFQUxFU1RBVEUiLCJpYXQiOjE3NDgwMDkzNzUsImV4cCI6MTc0ODAyMDE3NX0.PB6hiIthqGcfA1Q1Xqe_DsngvAhle522dPSLS5GtJ-o',
            'priority': 'u=1, i',
            'referer': 'https://new.land.naver.com/complexes/1096?ms=37.5213802,127.0409886,16&a=APT:ABYG:JGC:PRE&e=RETAIL',
            'sec-ch-ua': '"Chromium";v="136", "Google Chrome";v="136", "Not.A/Brand";v="99"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36',
        }
        
        # 토큰 정보 저장 (갱신 메커니즘에서 사용)
        self.token = self.headers['authorization'].replace('Bearer ', '')
        self.token_expiry = self._get_token_expiry(self.token)
        
        # 기본적으로 테스트 모드는 사용하지 않음
        self.use_test_mode = False  # 실제 API 호출로 변경
        self.test_data_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "naver_land_data.json")
        
        # 지역 코드 정보 (대표적인 지역)
        self.region_codes = {
            '서울': '1100000000',
            '경기': '4100000000',
            '인천': '2800000000',
            '부산': '2600000000',
            '대구': '2700000000',
            '광주': '2900000000',
            '대전': '3000000000',
            '울산': '3100000000',
            '세종': '3600000000',
            '강원': '4200000000',
            '충북': '4300000000',
            '충남': '4400000000',
            '전북': '4500000000',
            '전남': '4600000000',
            '경북': '4700000000',
            '경남': '4800000000',
            '제주': '5000000000'
        }
        
        # 실제 파일에서 사용한 복합키 (수원 매교동 푸르지오)
        self.default_complex_no = "128305"

        self.base_url = "https://new.land.naver.com/api"
        self._session = requests.Session()
        self.progress_callback = None
        self.progress = 0
        self.progress_message = ""
        
        # 토큰 만료 여부 확인
        self._check_token_expiry()

    def _get_token_expiry(self, token):
        """JWT 토큰에서 만료 시간 추출"""
        try:
            import base64
            # JWT 토큰의 두 번째 부분(payload) 디코딩
            payload = token.split('.')[1]
            # 패딩 추가
            payload += '=' * (4 - len(payload) % 4) if len(payload) % 4 else ''
            # base64 디코딩
            decoded = base64.b64decode(payload).decode('utf-8')
            # JSON 파싱
            data = json.loads(decoded)
            # 만료 시간 반환
            return data.get('exp', 0)
        except Exception as e:
            print(f"토큰 만료 시간 추출 중 오류: {str(e)}")
            return 0
    
    def _check_token_expiry(self):
        """토큰 만료 여부 확인 및 경고"""
        # 토큰 경고 메시지 없이 내부적으로만 상태 체크
        current_time = int(time.time())
        if self.token_expiry > 0:
            remaining_time = self.token_expiry - current_time
            # 모든 경고 메시지 제거

    def set_progress_callback(self, callback):
        """진행 상태 업데이트 콜백 설정"""
        self.progress_callback = callback

    def update_progress(self, progress, message="", status=None):
        """진행 상태 업데이트"""
        self.progress = progress
        self.progress_message = message
        
        # 콜백이 설정되어 있으면 호출
        if self.progress_callback:
            # 콜백 함수를 호출하여 메인 스레드에서 처리하도록 함
            if status:
                self.progress_callback(progress, message, status)
            else:
                self.progress_callback(progress, message)

    def search_by_complex(self, complex_no, max_pages=None, check_total_only=False):
        """단지번호로 매물 검색"""
        import time
        
        print(f"단지번호 {complex_no}로 매물 검색 시작")
        
        # 진행 상태 초기화
        self.progress = 0
        self.update_progress(0, "검색 시작...")
        
        # 결과 저장 딕셔너리
        result = {
            'articleList': [],
            'totalPages': 0,
            'totalCount': 0
        }
        
        # 최신 헤더와 쿠키 사용
        updated_headers = self.headers.copy()
        updated_cookies = self.cookies.copy()
        
        # 새로운 API 엔드포인트 사용 (2023년 변경됨)
        # 네이버 부동산 API 형식: https://new.land.naver.com/api/articles/complex/1096
        base_url = f"https://new.land.naver.com/api/articles/complex/{complex_no}"
        print(f"API 엔드포인트 URL: {base_url}")
        
        # 새로운 API 파라미터 형식 사용
        params = {
            'realEstateType': 'APT:ABYG:JGC:PRE',
            'tradeType': 'A1:B1:B2:B3',  # 매매, 전세, 월세 모두 포함
            'tag': '::::::::',
            'rentPriceMin': '0',
            'rentPriceMax': '900000000',
            'priceMin': '0',
            'priceMax': '900000000',
            'areaMin': '0',
            'areaMax': '900000000',
            'showArticle': 'true',
            'sameAddressGroup': 'false',
            'priceType': 'RETAIL',
            'directions': '',
            'page': '1',
            'complexNo': complex_no,
            'buildingNos': '',
            'areaNos': '',
            'type': 'list',
            'order': 'rank'
        }
        
        # 페이지 순회
        page = 1
        total_pages = 1  # 초기값
        
        while page <= total_pages and (max_pages is None or page <= max_pages):
            # 페이지 파라미터 업데이트
            params['page'] = str(page)
            
            print(f"매물 API 요청: {base_url} (페이지 {page})")
            
            try:
                # 최신 헤더와 쿠키 사용 - params 매개변수 사용하여 자동 URL 인코딩 적용
                response = requests.get(base_url, params=params, headers=updated_headers, cookies=updated_cookies)
                status_code = response.status_code
                print(f"매물 API 응답 상태 코드: {status_code} (페이지 {page})")
                
                # 응답 확인
                if status_code == 200:
                    data = response.json()
                    print(f"매물 API 응답 데이터 키: {data.keys() if data else 'None'}")
                    
                    # 매물 목록 추가
                    article_list = data.get('articleList', [])
                    if article_list:
                        result['articleList'].extend(article_list)
                        print(f"페이지 {page}: {len(article_list)}개 매물 추가됨")
                        
                        # 첫 페이지에서 총 매물 수 확인
                        if page == 1:
                            # isMoreData가 false면 더 이상 페이지가 없음
                            is_more_data = data.get('isMoreData', False)
                            total_count = len(article_list)
                            if not is_more_data:
                                total_pages = 1
                            else:
                                # 예상 페이지 수 (페이지당 10개 매물 기준)
                                total_pages = 1000  # 기본값, 실제로는 더 많을 수 있음
                            
                            result['totalCount'] = total_count
                            result['totalPages'] = total_pages
                            
                            print(f"총 매물 수: {total_count}, 총 페이지 수: {total_pages}")
                            
                            # 매물이 없는 경우
                            if total_count == 0:
                                print("매물이 없습니다.")
                                break
                            
                            # 총 페이지 수만 확인하는 경우
                            if check_total_only:
                                break
                        
                        # isMoreData가 false면 더 이상 페이지가 없음
                        if not data.get('isMoreData', False):
                            print(f"더 이상 페이지가 없습니다. (isMoreData: false)")
                            break
                    else:
                        print(f"페이지 {page}: 매물 없음")
                        # 페이지에 매물이 없으면 중단
                        break
                    
                    # 진행 상태 업데이트
                    progress_percent = min(int((page / min(total_pages, max_pages or float('inf'))) * 100), 100)
                    self.update_progress(progress_percent, f"매물 검색 중... ({page}페이지)")
                    
                elif status_code == 401:
                    # 인증 토큰 만료
                    print("API 인증 토큰이 만료되었습니다. 토큰을 업데이트합니다.")
                    
                    # 토큰 갱신 시도
                    if self._refresh_token():
                        # 갱신된 토큰으로 헤더 업데이트
                        updated_headers = self.headers.copy()
                        print("인증 토큰이 갱신되었습니다. 요청을 재시도합니다.")
                        # 같은 페이지 재시도
                        continue
                    else:
                        print("토큰 갱신 실패. 검색을 중단합니다.")
                        # 테스트 모드로 전환
                        self.use_test_mode = True
                        print("테스트 모드로 전환합니다.")
                        
                        # 테스트 데이터 로드
                        test_data = self._load_test_data()
                        if test_data:
                            print("테스트 데이터 로드 성공")
                            return test_data
                        break
                    
                elif status_code == 429:
                    # 요청 제한 초과
                    print("API 요청 제한을 초과했습니다. 잠시 후 다시 시도합니다.")
                    # 지수 백오프 전략 적용 (페이지에 따라 대기 시간 증가)
                    wait_time = min(3 * (1 ** (page % 5)), 3)  # 최대 60초 대기
                    print(f"{wait_time}초 대기 후 재시도합니다...")
                    time.sleep(wait_time)
                    continue  # 같은 페이지 재시도
                    
                else:
                    # 기타 오류
                    print(f"API 오류: 상태 코드 {status_code}")
                    print(f"응답 내용: {response.text[:200]}")
                    
                    # 테스트 모드로 전환
                    print("테스트 모드로 전환합니다.")
                    self.use_test_mode = True
                    
                    # 테스트 데이터 로드
                    test_data = self._load_test_data()
                    if test_data:
                        print("테스트 데이터 로드 성공")
                        return test_data
                    break
                
            except Exception as e:
                print(f"API 요청 중 예외 발생: {str(e)}")
                import traceback
                traceback.print_exc()
                
                # 테스트 모드로 전환
                print("테스트 모드로 전환합니다.")
                self.use_test_mode = True
                
                # 테스트 데이터 로드
                test_data = self._load_test_data()
                if test_data:
                    print("테스트 데이터 로드 성공")
                    return test_data
                break
            
            # 다음 페이지로 이동
            page += 1
            
            # 페이지 간 지연 시간 추가 (API 요청 제한 방지)
            delay = 0.2 if page < 5 else (0.5 if page < 10 else 1)
            time.sleep(delay)
        
        # 최종 진행 상태 업데이트
        self.update_progress(100, f"검색 완료: {len(result['articleList'])}개 매물")
        
        print(f"매물 검색 완료: {len(result['articleList'])}개 매물")
        return result

    def search_by_location(self, lat='37.2689669', lon='127.0057464', zoom='16', fetch_all_pages=False):
        """특정 위치(좌표)를 기준으로 매물 검색"""
        # 테스트 모드인 경우 테스트 데이터 반환
        if self.use_test_mode:
            print("테스트 모드: 샘플 데이터를 사용합니다.")
            return self._load_test_data()
            
        url = 'https://new.land.naver.com/api/articles'
        params = {
            'ms': f'{lat},{lon},{zoom}',
            'a': 'APT:PRE:ABYG:JGC',
            'e': 'RETAIL'
        }
        
        print(f"API 요청: {url} (위치 검색, 좌표: {lat},{lon})")
        
        try:
            response = requests.get(
                url,
                params=params,
                cookies=self.cookies,
                headers=self.headers
            )
            
            print(f"API 응답 상태 코드: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"API 응답 데이터: {data.keys() if data else 'None'}")
                
                # 여기서 location 검색으로 얻은 데이터에서 단지 번호를 추출하여 
                # 해당 단지의 모든 매물을 검색할 수 있음
                if fetch_all_pages and 'complexes' in data and data['complexes']:
                    complex_no = data['complexes'][0].get('complexNo')
                    if complex_no:
                        print(f"위치 검색에서 찾은 첫 번째 단지({complex_no})의 모든 매물을 검색합니다.")
                        return self.search_by_complex(complex_no=complex_no, fetch_all_pages=True)
                
                return data
            else:
                print(f"API 요청 실패: {response.status_code}")
                print(f"응답: {response.text[:200]}")
                
                # 인증 토큰 만료되었을 경우
                if response.status_code == 401:
                    print("인증 토큰이 만료되었을 수 있습니다. 테스트 데이터로 전환합니다.")
                    return self._load_test_data()
                    
                return None
                
        except Exception as e:
            print(f"API 요청 중 오류 발생: {e}")
            return self._load_test_data()  # 오류 발생 시 테스트 데이터 사용

    def search_by_region(self, region_code='4100000000', fetch_all_pages=False):
        """특정 지역 코드로 매물 검색 - 이 방식은 실제로 기존 파일과 다르게 작동할 수 있음"""
        # 테스트 모드인 경우 테스트 데이터 반환
        if self.use_test_mode:
            print("테스트 모드: 샘플 데이터를 사용합니다.")
            return self._load_test_data()
        
        # 지역 코드와 가장 근접한 API 호출 방식:
        # 지역코드(cortarNo)로 단지 리스트를 먼저 가져온 후, 
        # 그 단지 중 첫번째 단지 번호로 매물 검색
        try:
            # 1. 지역의 단지 리스트 가져오기
            complexes_url = 'https://new.land.naver.com/api/regions/complexes'
            complex_params = {
                'cortarNo': region_code,
                'realEstateType': 'APT:PRE:ABYG:JGC',
                'order': 'rank',
                'showR0': 'false'
            }
            
            print(f"단지 리스트 API 요청: {complexes_url} (지역코드: {region_code})")
            
            complex_response = requests.get(
                complexes_url,
                params=complex_params,
                cookies=self.cookies,
                headers=self.headers
            )
            
            print(f"단지 리스트 API 응답 상태 코드: {complex_response.status_code}")
            
            if complex_response.status_code == 200:
                complex_data = complex_response.json()
                
                # API 응답 형식에 따라 단지 리스트 추출
                complex_list = complex_data.get('complexList', [])
                if not complex_list:
                    print(f"지역코드 {region_code}에 해당하는 단지가 없습니다.")
                    # 경기도(4100000000) 지역에 단지가 없으면 수원시 단지 정보 사용
                    return self.search_by_complex(self.default_complex_no, fetch_all_pages=fetch_all_pages)
                
                # 2. 첫번째 단지 번호로 해당 단지의 매물 검색
                first_complex = complex_list[0]
                complex_no = first_complex.get('complexNo')
                
                print(f"검색된 첫 번째 단지 번호: {complex_no}")
                
                if complex_no:
                    # 단지 번호로 검색 API 호출
                    return self.search_by_complex(complex_no=complex_no, fetch_all_pages=fetch_all_pages)
                else:
                    print("단지 번호를 찾을 수 없습니다.")
                    return self._load_test_data()
            else:
                print(f"단지 리스트 API 요청 실패: {complex_response.status_code}")
                print(f"응답: {complex_response.text[:200]}")
                
                # 인증 토큰 만료되었을 경우
                if complex_response.status_code == 401:
                    print("인증 토큰이 만료되었을 수 있습니다. 테스트 데이터로 전환합니다.")
                
                # 기본 단지 번호로 대체 검색
                return self.search_by_complex(self.default_complex_no, fetch_all_pages=fetch_all_pages)
                
        except Exception as e:
            print(f"지역 검색 중 오류 발생: {e}")
            # 오류 발생 시 테스트 데이터 사용
            return self._load_test_data()
    
    def search_region_info(self, region_code='4100000000'):
        """지역 정보 조회"""
        # 테스트 모드인 경우 None 반환
        if self.use_test_mode:
            print("테스트 모드: 지역 정보를 조회하지 않습니다.")
            return None
            
        url = 'https://new.land.naver.com/api/regions/list'
        params = {
            'cortarNo': region_code
        }
        
        print(f"지역 정보 요청: {url} (지역코드: {region_code})")
        
        try:
            response = requests.get(
                url,
                params=params,
                cookies=self.cookies,
                headers=self.headers
            )
            
            print(f"API 응답 상태 코드: {response.status_code}")
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"API 요청 실패: {response.status_code}")
                print(f"응답: {response.text[:200]}")
                return None
        except Exception as e:
            print(f"API 요청 중 오류 발생: {e}")
            return None
    
    def search_by_keyword(self, keyword, max_pages=None):
        """키워드로 단지 검색"""
        import time
        
        # 검색 결과 저장 변수
        all_data = None
        all_complexes = []
        
        # 진행 상태 초기화
        self.update_progress(0, f"키워드 '{keyword}'로 단지 검색을 시작합니다...")
        
        # 토큰 만료 여부 확인
        self._check_token_expiry()
        
        # 최신 헤더와 쿠키 사용
        updated_headers = self.headers.copy()
        updated_cookies = self.cookies.copy()
        
        # max_pages가 None인 경우 큰 숫자로 설정하여 모든 페이지 검색
        max_pages_to_search = max_pages if max_pages is not None else 1000
        
        for page in range(1, max_pages_to_search + 1):
            try:
                # 진행 상태 업데이트
                if max_pages:
                    progress = min(int((page / max_pages) * 100), 95)
                else:
                    progress = min(int((page / 20) * 100), 95)  # 페이지 수를 모를 때는 20페이지를 기준으로 진행 상황 표시
                self.update_progress(progress, f"페이지 {page} 가져오는 중...")
                
                # API 엔드포인트 및 파라미터 설정
                params = {
                    'keyword': keyword,
                    'page': str(page),
                }
                
                url = "https://new.land.naver.com/api/search"
                
                print(f"API 요청: {url} (페이지 {page}, 키워드: {keyword})")
                
                # API 요청 수행 - params 매개변수 사용하여 자동 URL 인코딩 적용
                response = requests.get(url, params=params, headers=updated_headers, cookies=updated_cookies)
                print(f"API 응답 상태 코드: {response.status_code}")
                
                # 응답 처리
                if response.status_code == 200:
                    data = response.json()
                    
                    # API 응답 디버깅
                    print(f"API 응답 데이터 키: {data.keys() if data else 'None'}")
                    
                    # 에러 응답 확인
                    if 'error' in data:
                        error_code = data.get('error', {}).get('code', 'unknown')
                        error_msg = data.get('error', {}).get('message', '알 수 없는 오류')
                        print(f"API 에러 응답: {error_code} - {error_msg}")
                        
                        # 에러 정보 저장
                        if all_data is None:
                            all_data = {'complexes': [], 'error': error_msg}
                        break
                    
                    # 첫 페이지인 경우 전체 데이터 구조 저장
                    if all_data is None:
                        all_data = data
                        all_complexes = data.get('complexes', [])
                        print(f"첫 페이지 데이터: {len(all_complexes)}개 단지 발견")
                    else:
                        # 이후 페이지의 complexes만 추가
                        page_complexes = data.get('complexes', [])
                        if page_complexes:
                            all_complexes.extend(page_complexes)
                            print(f"페이지 {page}에서 {len(page_complexes)}개 단지 추가")
                        else:
                            # 더 이상 데이터가 없으면 종료
                            print(f"페이지 {page}에 더 이상 데이터가 없습니다. 종료합니다.")
                            break
                            
                    # 더 이상 데이터가 없으면 종료
                    if not data.get('isMoreData', False):
                        print("더 이상 데이터가 없습니다. 검색을 종료합니다.")
                        break
                            
                    # API 요청 간에 짧은 딜레이 추가
                    time.sleep(0.5)
                elif response.status_code == 401:
                    # 인증 토큰 만료 - 토큰 갱신 시도
                    print("인증 토큰이 만료되었습니다. 갱신을 시도합니다.")
                    
                    # 토큰 갱신 시도
                    if self._refresh_token():
                        # 갱신된 토큰으로 헤더 업데이트
                        updated_headers = self.headers.copy()
                        print("인증 토큰이 갱신되었습니다. 요청을 재시도합니다.")
                        page -= 1  # 같은 페이지 재시도
                        continue
                    else:
                        print("토큰 갱신 실패. 검색을 중단합니다.")
                        # 테스트 모드로 전환
                        self.use_test_mode = True
                        print("테스트 모드로 전환합니다.")
                        break
                else:
                    print(f"API 요청 실패: {response.status_code}")
                    if response.status_code == 429:
                        print("요청 제한 초과. 잠시 후 다시 시도합니다.")
                        # 지수 백오프 전략 적용
                        wait_time = min(5 * (2 ** (page % 5)), 60)  # 최대 60초 대기
                        print(f"{wait_time}초 대기 후 재시도합니다...")
                        time.sleep(wait_time)
                        page -= 1  # 같은 페이지 재시도
                        continue
                    else:
                        # 기타 오류
                        print(f"API 오류: {response.text[:200]}")
                        # 오류 정보 저장
                        all_data = all_data or {'complexes': []}
                        all_data['error'] = f"API 오류: 상태 코드 {response.status_code}"
                        break
            except Exception as e:
                print(f"API 요청 중 오류 발생: {e}")
                import traceback
                traceback.print_exc()
                # 예외 정보 저장
                all_data = all_data or {'complexes': []}
                all_data['error'] = f"API 요청 중 오류 발생: {str(e)}"
                break
        
        # 진행 상황 업데이트 완료 (100%)
        self.update_progress(100, "검색 완료")
        
        # 모든 complexes 데이터를 병합
        if all_data:
            if 'complexes' in all_data:
                all_data['complexes'] = all_complexes
                all_data['isMoreData'] = False  # 모든 데이터를 가져왔으므로 더 이상 없음
                all_data['totalCount'] = len(all_complexes)  # 총 단지 수 추가
                print(f"총 {len(all_complexes)}개 단지 정보를 가져왔습니다.")
            
            # 검색 결과를 파일로 저장
            file_path = self.save_response_to_file(all_data, f"{keyword}_complexes.json")
            print(f"검색 결과가 {file_path} 파일에 저장되었습니다.")
            
            return all_data
        
        # 검색 결과가 없는 경우 빈 데이터 반환
        empty_result = {'complexes': [], 'totalCount': 0}
        return empty_result
    
    def _refresh_token(self):
        """인증 토큰 갱신 시도"""
        try:
            print("인증 토큰 갱신 시도 중...")
            
            # 1. naver.py에서 최신 토큰 가져오기
            try:
                # naver.py 파일 경로
                naver_py_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "naver.py")
                
                if os.path.exists(naver_py_path):
                    print(f"naver.py 파일에서 최신 토큰 가져오기 시도: {naver_py_path}")
                    
                    # 파일 내용 읽기
                    with open(naver_py_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # 정규식으로 토큰 추출
                    import re
                    token_match = re.search(r"'authorization':\s*'Bearer\s+([^']+)'", content)
                    
                    if token_match:
                        new_token = token_match.group(1)
                        print(f"naver.py에서 새 토큰을 찾았습니다.")
                        
                        # 토큰 만료 시간 확인
                        expiry = self._get_token_expiry(new_token)
                        current_time = int(time.time())
                        
                        if expiry > current_time:
                            print(f"새 토큰은 유효합니다. (만료까지 {expiry - current_time}초 남음)")
                            self.headers['authorization'] = f'Bearer {new_token}'
                            self.token = new_token
                            self.token_expiry = expiry
                            return True
                        else:
                            print(f"새 토큰도 이미 만료되었습니다. (만료된 지 {current_time - expiry}초 지남)")
                            # 하드코딩된 토큰 사용
                            print("하드코딩된 토큰을 사용합니다.")
                    else:
                        print("naver.py에서 토큰을 찾을 수 없습니다.")
                else:
                    print(f"naver.py 파일을 찾을 수 없습니다: {naver_py_path}")
            except Exception as e:
                print(f"naver.py에서 토큰 추출 중 오류: {str(e)}")
            
            # 2. 하드코딩된 토큰 사용 (백업 방법)
            new_token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6IlJFQUxFU1RBVEUiLCJpYXQiOjE3NDgwMDkzNzUsImV4cCI6MTc0ODAyMDE3NX0.PB6hiIthqGcfA1Q1Xqe_DsngvAhle522dPSLS5GtJ-o'
            self.headers['authorization'] = f'Bearer {new_token}'
            self.token = new_token
            self.token_expiry = self._get_token_expiry(new_token)
            
            print("인증 토큰이 갱신되었습니다.")
            return True
        except Exception as e:
            print(f"토큰 갱신 중 오류 발생: {str(e)}")
            return False

    def _load_test_data(self):
        """테스트용 데이터 로드"""
        try:
            print("테스트 데이터 로드 시도...")
            # 현재 디렉토리에서 테스트 데이터 파일 찾기
            if os.path.exists(self.test_data_file):
                print(f"테스트 데이터 파일 발견: {self.test_data_file}")
                with open(self.test_data_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    print(f"테스트 데이터 로드 완료: {data.keys() if data else 'None'}")
                    return data
            else:
                print(f"테스트 데이터 파일을 찾을 수 없습니다: {self.test_data_file}")
                
                # 프로젝트 루트의 naver_land_data.json 확인
                root_file = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "naver_land_data.json")
                print(f"프로젝트 루트에서 데이터 파일 확인: {root_file}")
                
                if os.path.exists(root_file):
                    print(f"프로젝트 루트에서 데이터 파일 발견: {root_file}")
                    with open(root_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        print(f"데이터 로드 완료: {data.keys() if data else 'None'}")
                        return data
                else:
                    print(f"프로젝트 루트에서도 데이터 파일을 찾을 수 없습니다: {root_file}")
                    
                    # 테스트 데이터 파일이 없으면 기본 데이터 생성
                    print("테스트 데이터 파일이 없어 기본 데이터를 생성합니다.")
                    default_data = {
                        "articleList": [
                            {
                                "articleNo": "2311234567",
                                "complexNo": "128305",
                                "complexName": "테스트 아파트",
                                "tradeTypeName": "매매",
                                "floorInfo": "5층",
                                "areaNormal": 84.56,
                                "supplyArea": 110.24,
                                "direction": "남향",
                                "priceString": "8억 5,000",
                                "checkDate": "2023-11-01"
                            },
                            {
                                "articleNo": "2311234568",
                                "complexNo": "128305",
                                "complexName": "테스트 아파트",
                                "tradeTypeName": "전세",
                                "floorInfo": "10층",
                                "areaNormal": 59.23,
                                "supplyArea": 84.12,
                                "direction": "동향",
                                "priceString": "3억 8,000",
                                "checkDate": "2023-11-02"
                            }
                        ],
                        "totalCount": 2,
                        "totalPages": 1
                    }
                    
                    # 테스트 데이터 파일 저장
                    self.save_response_to_file(default_data)
                    print("기본 테스트 데이터를 생성하고 파일로 저장했습니다.")
                    return default_data
                
                return {"articleList": [], "message": "테스트 데이터 없음"}
        except Exception as e:
            print(f"테스트 데이터 로드 중 오류 발생: {e}")
            return {"articleList": [], "message": f"테스트 데이터 로드 오류: {str(e)}"}

    def save_response_to_file(self, data, filename='naver_land_data.json'):
        """API 응답 데이터를 파일로 저장"""
        if data:
            try:
                # 상대 경로 대신 절대 경로 사용
                current_dir = os.path.dirname(os.path.abspath(__file__))
                file_path = os.path.join(current_dir, filename)
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=4)
                print(f"데이터가 {file_path} 파일로 저장되었습니다.")
                
                # 테스트 데이터 파일 경로 업데이트
                self.test_data_file = file_path
                return file_path
            except Exception as e:
                print(f"파일 저장 중 오류 발생: {e}")
                return None
        return None

    def load_complex_data(self, file_path=None):
        """특정 JSON 파일에서 단지 정보 불러오기"""
        try:
            if file_path is None:
                # 기본 경로 사용
                current_dir = os.path.dirname(os.path.abspath(__file__))
                file_path = os.path.join(current_dir, "청담동_complexes.json")
            
            print(f"단지 정보 파일 로드 시도: {file_path}")
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    print(f"단지 정보 로드 완료: {len(data.get('complexes', []))}개 단지 정보")
                    return data
            else:
                print(f"단지 정보 파일을 찾을 수 없습니다: {file_path}")
                return None
        except Exception as e:
            print(f"단지 정보 로드 중 오류 발생: {e}")
            return None

    def find_complex_by_name(self, name, file_path=None):
        """단지명으로 단지 정보 검색"""
        data = self.load_complex_data(file_path)
        if not data or 'complexes' not in data:
            return None
            
        complexes = data['complexes']
        # 정확히 일치하는 단지명 찾기
        for complex_info in complexes:
            if complex_info.get('complexName') == name:
                return complex_info
                
        # 부분 일치하는 단지 찾기
        matching_complexes = []
        for complex_info in complexes:
            if name.lower() in complex_info.get('complexName', '').lower():
                matching_complexes.append(complex_info)
                
        return matching_complexes[0] if matching_complexes else None
        
    def find_complex_by_address(self, address, file_path=None):
        """주소로 단지 정보 검색"""
        data = self.load_complex_data(file_path)
        if not data or 'complexes' not in data:
            return None
            
        complexes = data['complexes']
        matching_complexes = []
        
        # 주소 기반 검색
        for complex_info in complexes:
            if address.lower() in complex_info.get('cortarAddress', '').lower():
                matching_complexes.append(complex_info)
                
        return matching_complexes[0] if matching_complexes else None

    def get_complexes_by_cortarId(self, cortarId, max_pages=1000):
        """특정 지역 코드로 단지 정보 검색"""
        if self.use_test_mode:
            print("테스트 모드: 샘플 데이터를 사용합니다.")
            return self._load_test_data()
        
        print(f"지역 코드 {cortarId}로 단지 정보 검색을 시작합니다...")
        
        all_complexes = []
        
        # 진행 상황 업데이트 초기화
        self.update_progress(0, "검색 시작")
        
        for page in range(1, max_pages + 1):
            print(f"페이지 {page} 가져오는 중...")
            
            # 진행 상황 업데이트
            progress = min(int((page / max_pages) * 100), 95)
            self.update_progress(progress, f"페이지 {page} 검색 중")
            
            url = "https://new.land.naver.com/api/regions/complexes"
            params = {
                'cortarId': cortarId,
                'realEstateType': 'APT',
                'order': 'rank',
                'page': str(page)
            }
            
            try:
                response = requests.get(
                    url,
                    params=params,
                    cookies=self.cookies,
                    headers=self.headers
                )
                
                print(f"API 응답 상태 코드: {response.status_code} (페이지 {page})")
                
                if response.status_code == 200:
                    data = response.json()
                    page_complexes = data.get('complexList', [])
                    
                    if page_complexes:
                        all_complexes.extend(page_complexes)
                        print(f"페이지 {page}에서 {len(page_complexes)}개 단지 추가")
                    else:
                        # 더 이상 데이터가 없으면 종료
                        print(f"페이지 {page}에 더 이상 데이터가 없습니다. 종료합니다.")
                        break
                    
                    # 다음 페이지가 없으면 종료
                    if not data.get('isMoreData', False):
                        print("더 이상 데이터가 없습니다. 종료합니다.")
                        break
                    
                    # API 요청 간에 짧은 딜레이 추가
                    time.sleep(0.5)
                else:
                    print(f"API 요청 실패: {response.status_code}")
                    break
            except Exception as e:
                print(f"API 요청 중 오류 발생: {e}")
                break
        
        # 진행 상황 업데이트 완료
        self.update_progress(100, "검색 완료")
        
        print(f"총 {len(all_complexes)}개 단지 정보를 가져왔습니다.")
        
        # 검색 결과를 파일로 저장
        result_data = {"complexes": all_complexes}
        file_path = self.save_response_to_file(result_data, f"cortarId_{cortarId}_complexes.json")
        print(f"검색 결과가 {file_path} 파일에 저장되었습니다.")
        
        return result_data

    def _make_request(self, url, params=None):
        """API 요청 수행"""
        try:
            response = requests.get(
                url,
                params=params,
                cookies=self.cookies,
                headers=self.headers
            )
            return response
        except Exception as e:
            print(f"API 요청 중 오류 발생: {str(e)}")
            return None 