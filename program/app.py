"""
본 프로그램 'RankChecker by ORYNE'는 ORYNE에 의해 개발된 소프트웨어입니다.
해당 소스코드 및 실행 파일의 무단 복제, 배포, 역컴파일, 수정은
저작권법 및 컴퓨터프로그램 보호법에 따라 엄격히 금지됩니다.

무단 유포 및 상업적 이용 시 민형사상 법적 책임을 물을 수 있습니다.

Copyright ⓒ 2025 ORYNE. All rights reserved.
Unauthorized reproduction or redistribution is strictly prohibited. 
"""

import os
import json
import urllib.request
import urllib.parse
import re
import streamlit as st
from dotenv import load_dotenv
from PIL import Image

# Load environment variables
load_dotenv()

client_id = os.getenv("NAVER_CLIENT_ID")
client_secret = os.getenv("NAVER_CLIENT_SECRET")

# 광고 API 키 (연관 키워드용)
CUSTOMER_ID = os.getenv("CUSTOMER_ID")
ACCESS_LICENSE = os.getenv("ACCESS_LICENSE")
SECRET_KEY = os.getenv("SECRET_KEY")

# 파비콘 로드
try:
    logo_path = os.path.join(os.path.dirname(__file__), "..", "..", "assets", "oryne_logo.png")
    favicon = Image.open(logo_path)
except:
    favicon = "🔍"  # 파일을 찾을 수 없으면 이모지 사용

# 페이지 설정
st.set_page_config(
    page_title="네이버 키워드 도구 by ORYNE",
    page_icon=favicon,
    layout="centered",
    initial_sidebar_state="collapsed"
)

# 다크모드 감지 및 커스텀 CSS
st.markdown("""
<style>
    /* 라이트 모드 */
    [data-testid="stAppViewContainer"] {
        --success-bg-light: #d4edda;
        --success-border-light: #c3e6cb;
        --success-text-light: #155724;
        --error-bg-light: #f8d7da;
        --error-border-light: #f5c6cb;
        --error-text-light: #721c24;
    }
    
    /* 다크 모드 */
    [data-theme="dark"] {
        --success-bg-dark: #1e4620;
        --success-border-dark: #2d5a2f;
        --success-text-dark: #a8e6a3;
        --error-bg-dark: #4a1f1f;
        --error-border-dark: #6b2c2c;
        --error-text-dark: #f5a3a3;
    }
    
    .main-header {
        text-align: center;
        color: #1f77b4;
        padding: 1rem 0;
    }
    
    .footer {
        text-align: center;
        color: gray;
        font-size: 12px;
        padding: 2rem 0;
    }
    
    .result-box {
        padding: 1.5rem;
        border-radius: 8px;
        margin: 0.8rem 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    /* 라이트 모드 - 성공 박스 */
    [data-testid="stAppViewContainer"]:not([data-theme="dark"]) .success-box {
        background-color: #d4edda;
        border: 2px solid #28a745;
        color: #155724;
    }
    
    [data-testid="stAppViewContainer"]:not([data-theme="dark"]) .success-box h4 {
        color: #155724;
        font-weight: bold;
    }
    
    [data-testid="stAppViewContainer"]:not([data-theme="dark"]) .success-box strong {
        color: #0d3d17;
    }
    
    /* 라이트 모드 - 에러 박스 */
    [data-testid="stAppViewContainer"]:not([data-theme="dark"]) .error-box {
        background-color: #f8d7da;
        border: 2px solid #dc3545;
        color: #721c24;
    }
    
    [data-testid="stAppViewContainer"]:not([data-theme="dark"]) .error-box h4 {
        color: #721c24;
        font-weight: bold;
    }
    
    /* 다크 모드 - 성공 박스 */
    [data-theme="dark"] .success-box {
        background-color: #1e4620 !important;
        border: 2px solid #3d8b40 !important;
        color: #c8f5c8 !important;
    }
    
    [data-theme="dark"] .success-box h4 {
        color: #a8e6a3 !important;
        font-weight: bold;
    }
    
    [data-theme="dark"] .success-box strong {
        color: #d4ffd4 !important;
    }
    
    [data-theme="dark"] .success-box li {
        color: #c8f5c8 !important;
    }
    
    [data-theme="dark"] .success-box a {
        color: #5dade2 !important;
    }
    
    /* 다크 모드 - 에러 박스 */
    [data-theme="dark"] .error-box {
        background-color: #4a1f1f !important;
        border: 2px solid #8b3d3d !important;
        color: #f5c8c8 !important;
    }
    
    [data-theme="dark"] .error-box h4 {
        color: #f5a3a3 !important;
        font-weight: bold;
    }
    
    [data-theme="dark"] .error-box p {
        color: #f5c8c8 !important;
    }
    
    /* 링크 스타일 개선 */
    .result-box a {
        text-decoration: none;
        font-weight: bold;
        transition: all 0.3s ease;
    }
    
    .result-box a:hover {
        text-decoration: underline;
        opacity: 0.8;
    }
    
    /* 리스트 스타일 개선 */
    .result-box ul {
        list-style: none;
        padding-left: 0;
    }
    
    .result-box li {
        padding: 0.3rem 0;
        line-height: 1.6;
    }
</style>
""", unsafe_allow_html=True)

def get_related_keywords(keyword):
    """네이버 광고 API를 통해 연관 키워드 검색"""
    import base64
    import hmac
    import hashlib
    import time
    
    timestamp = str(int(time.time() * 1000))
    method = "GET"
    uri = "/keywordstool"
    
    # 서명 생성
    message = f"{timestamp}.{method}.{uri}"
    signature = base64.b64encode(
        hmac.new(
            SECRET_KEY.encode('utf-8'),
            message.encode('utf-8'),
            hashlib.sha256
        ).digest()
    ).decode('utf-8')
    
    url = f"https://api.naver.com/keywordstool?hintKeywords={urllib.parse.quote(keyword)}&showDetail=1"
    
    headers = {
        "X-Timestamp": timestamp,
        "X-API-KEY": ACCESS_LICENSE,
        "X-Customer": CUSTOMER_ID,
        "X-Signature": signature
    }
    
    try:
        request = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(request) as response:
            result = json.loads(response.read().decode('utf-8'))
            return result.get('keywordList', [])
    except Exception as e:
        st.error(f"연관 키워드 검색 중 오류: {e}")
        return []

def get_keyword_stats(keyword):
    """네이버 쇼핑 API로 키워드 통계 가져오기"""
    try:
        encText = urllib.parse.quote(keyword)
        url = f"https://openapi.naver.com/v1/search/shop.json?query={encText}&display=1"
        request = urllib.request.Request(url)
        request.add_header("X-Naver-Client-Id", client_id)
        request.add_header("X-Naver-Client-Secret", client_secret)
        response = urllib.request.urlopen(request)
        result = json.loads(response.read())
        return result.get('total', 0)
    except:
        return 0

def get_top_ranked_product_by_mall(keyword, mall_name, progress_bar=None):
    """네이버 쇼핑 API를 통해 특정 쇼핑몰의 최상위 상품 검색"""
    encText = urllib.parse.quote(keyword)
    seen_titles = set()
    best_product = None
    
    total_pages = 10  # 1000개 검색 (100개씩 10페이지)
    
    for page_num, start in enumerate(range(1, 1001, 100), 1):
        url = f"https://openapi.naver.com/v1/search/shop.json?query={encText}&display=100&start={start}"
        request = urllib.request.Request(url)
        request.add_header("X-Naver-Client-Id", client_id)
        request.add_header("X-Naver-Client-Secret", client_secret)
        
        try:
            response = urllib.request.urlopen(request)
            result = json.loads(response.read())
            
            for idx, item in enumerate(result.get("items", []), start=1):
                if item.get("mallName") and mall_name in item["mallName"]:
                    title_clean = re.sub(r"<.*?>", "", item["title"])
                    if title_clean in seen_titles:
                        continue
                    seen_titles.add(title_clean)
                    rank = start + idx - 1
                    product = {
                        "rank": rank,
                        "title": title_clean,
                        "price": item["lprice"],
                        "link": item["link"],
                        "mallName": item["mallName"]
                    }
                    if not best_product or rank < best_product["rank"]:
                        best_product = product
            
            # 진행률 업데이트
            if progress_bar:
                progress_bar.progress(page_num / total_pages)
                
        except Exception as e:
            st.error(f"API 호출 중 오류 발생: {e}")
            break
    
    return best_product

def main():
    # 헤더에 로고 추가
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        try:
            st.image("../../assets/oryne_logo.png", width="stretch")
        except:
            # 로고 파일이 없을 경우 텍스트로 대체
            st.markdown("<h1 class='main-header'>🔍 네이버 키워드 도구</h1>", unsafe_allow_html=True)
    
    st.markdown("<p style='text-align: center; color: gray; margin-top: -1rem;'>by ORYNE</p>", unsafe_allow_html=True)
    
    st.markdown("---")
    
    # 탭 생성
    tab1, tab2, tab3 = st.tabs(["🎯 순위 확인", "🔑 연관 키워드", "📊 키워드 분석"])
    
    # 탭 1: 순위 확인
    with tab1:
        rank_checker_tab()
    
    # 탭 2: 연관 키워드
    with tab2:
        related_keywords_tab()
    
    # 탭 3: 키워드 분석
    with tab3:
        keyword_analysis_tab()
    
    # 푸터
    st.markdown("---")
    st.markdown(
        "<div class='footer'>ⓒ 2025 ORYNE. 무단 복제 및 배포 금지. All rights reserved.</div>",
        unsafe_allow_html=True
    )
    
    # 사이드바 정보
    sidebar_info()

def rank_checker_tab():
    """순위 확인 탭"""
    st.subheader("📝 검색 정보 입력")
    
    # 검색어 입력
    keywords_input = st.text_area(
        "검색어 (최대 10개, 쉼표로 구분)",
        placeholder="예: 키보드, 마우스, 충전기",
        height=100,
        help="검색하고자 하는 키워드를 쉼표(,)로 구분하여 입력하세요"
    )
    
    # 판매처명 입력
    mall_name = st.text_input(
        "판매처명",
        placeholder="예: OO스토어",
        help="검색하고자 하는 쇼핑몰 이름을 입력하세요"
    )
    
    # 검색 버튼
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        search_button = st.button("🔍 순위 확인", width="stretch", type="primary")
    
    # 검색 실행
    if search_button:
        # 입력 검증
        keywords = [k.strip() for k in keywords_input.split(",") if k.strip()]
        
        if not keywords or not mall_name:
            st.error("⚠️ 검색어와 판매처명을 모두 입력하세요.")
            return
        
        if len(keywords) > 10:
            st.error("⚠️ 검색어는 최대 10개까지 가능합니다.")
            return
        
        # 검색 진행
        st.markdown("---")
        st.subheader("📊 검색 결과")
        
        # 전체 진행률
        overall_progress = st.progress(0)
        status_text = st.empty()
        
        results = {}
        
        for idx, keyword in enumerate(keywords, 1):
            status_text.text(f"🔄 검색 중... ({idx}/{len(keywords)}) - {keyword}")
            
            # 개별 키워드 진행률
            with st.expander(f"🔍 {keyword}", expanded=True):
                keyword_progress = st.progress(0)
                result = get_top_ranked_product_by_mall(keyword, mall_name, keyword_progress)
                
                if result:
                    st.markdown(f"""
                    <div class='result-box success-box'>
                        <h4>✅ {keyword}</h4>
                        <ul>
                            <li><strong>순위:</strong> {result['rank']}위</li>
                            <li><strong>상품명:</strong> {result['title']}</li>
                            <li><strong>가격:</strong> {int(result['price']):,}원</li>
                            <li><strong>쇼핑몰:</strong> {result['mallName']}</li>
                            <li><strong>링크:</strong> <a href="{result['link']}" target="_blank">상품 보기</a></li>
                        </ul>
                    </div>
                    """, unsafe_allow_html=True)
                    results[keyword] = result
                else:
                    st.markdown(f"""
                    <div class='result-box error-box'>
                        <h4>❌ {keyword}</h4>
                        <p>검색 결과 없음 (상위 1000개 내에 해당 판매처의 상품이 없습니다)</p>
                    </div>
                    """, unsafe_allow_html=True)
                    results[keyword] = None
            
            # 전체 진행률 업데이트
            overall_progress.progress(idx / len(keywords))
        
        # 완료 메시지
        status_text.text("✅ 모든 검색이 완료되었습니다!")
        
        # 요약 정보
        st.markdown("---")
        st.subheader("📈 검색 요약")
        
        found_count = sum(1 for v in results.values() if v is not None)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("총 검색어", len(keywords))
        with col2:
            st.metric("발견", found_count)
        with col3:
            st.metric("미발견", len(keywords) - found_count)
        
        # 로그 출력 (콘솔)
        print(f"검색 완료: {mall_name}, 키워드: {', '.join(keywords)}")
        print(f"결과 개수: {len(results)}")

def related_keywords_tab():
    """연관 키워드 검색 탭"""
    st.subheader("🔑 연관 키워드 검색")
    st.info("입력한 키워드와 관련된 다양한 키워드를 찾아드립니다.")
    
    # 키워드 입력
    keyword = st.text_input(
        "기본 키워드 입력",
        placeholder="예: 노트북",
        help="연관 키워드를 찾을 기본 키워드를 입력하세요"
    )
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        search_button = st.button("🔍 연관 키워드 검색", width="stretch", type="primary", key="related_search")
    
    if search_button and keyword:
        with st.spinner("연관 키워드를 검색 중입니다..."):
            if CUSTOMER_ID and ACCESS_LICENSE and SECRET_KEY:
                related_keywords = get_related_keywords(keyword)
                
                if related_keywords:
                    st.success(f"✅ {len(related_keywords)}개의 연관 키워드를 찾았습니다!")
                    
                    # 테이블 형식으로 표시
                    st.markdown("---")
                    st.subheader("📋 연관 키워드 목록")
                    
                    for idx, kw_data in enumerate(related_keywords[:50], 1):  # 상위 50개만 표시
                        kw = kw_data.get('relKeyword', '')
                        monthly_pc = kw_data.get('monthlyPcQcCnt', 0)
                        monthly_mobile = kw_data.get('monthlyMobileQcCnt', 0)
                        monthly_total = monthly_pc + monthly_mobile
                        
                        with st.expander(f"#{idx} {kw} (월간 검색량: {monthly_total:,})"):
                            col1, col2, col3 = st.columns(3)
                            with col1:
                                st.metric("PC 검색", f"{monthly_pc:,}")
                            with col2:
                                st.metric("모바일 검색", f"{monthly_mobile:,}")
                            with col3:
                                st.metric("총 검색", f"{monthly_total:,}")
                else:
                    st.warning("연관 키워드를 찾을 수 없습니다.")
            else:
                st.error("⚠️ 네이버 광고 API 키가 설정되지 않았습니다. .env 파일을 확인하세요.")
    elif search_button:
        st.warning("⚠️ 키워드를 입력해주세요.")

def keyword_analysis_tab():
    """키워드 분석 탭"""
    st.subheader("📊 키워드 분석 도구")
    st.info("여러 키워드의 경쟁 상황을 한눈에 비교할 수 있습니다.")
    
    # 키워드 입력
    keywords_input = st.text_area(
        "분석할 키워드 입력 (최대 20개, 쉼표로 구분)",
        placeholder="예: 노트북, 게이밍노트북, 사무용노트북",
        height=100,
        help="비교 분석하고 싶은 키워드를 쉼표로 구분하여 입력하세요"
    )
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        analyze_button = st.button("📊 키워드 분석", width="stretch", type="primary", key="analyze")
    
    if analyze_button:
        keywords = [k.strip() for k in keywords_input.split(",") if k.strip()]
        
        if not keywords:
            st.error("⚠️ 분석할 키워드를 입력하세요.")
            return
        
        if len(keywords) > 20:
            st.error("⚠️ 키워드는 최대 20개까지 분석 가능합니다.")
            return
        
        # 분석 시작
        st.markdown("---")
        st.subheader("📈 키워드 분석 결과")
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        results = []
        
        for idx, keyword in enumerate(keywords, 1):
            status_text.text(f"🔄 분석 중... ({idx}/{len(keywords)}) - {keyword}")
            
            # 네이버 쇼핑 검색 결과 수
            total_count = get_keyword_stats(keyword)
            
            results.append({
                "키워드": keyword,
                "검색 결과 수": total_count,
                "경쟁도": "높음" if total_count > 10000 else "보통" if total_count > 1000 else "낮음"
            })
            
            progress_bar.progress(idx / len(keywords))
        
        status_text.text("✅ 분석 완료!")
        
        # 결과를 데이터프레임으로 표시
        import pandas as pd
        df = pd.DataFrame(results)
        df = df.sort_values("검색 결과 수", ascending=False)
        
        st.dataframe(
            df,
            width="stretch",
            hide_index=True
        )
        
        # 요약 통계
        st.markdown("---")
        st.subheader("📊 분석 요약")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("분석 키워드 수", len(keywords))
        with col2:
            avg_count = sum(r["검색 결과 수"] for r in results) / len(results)
            st.metric("평균 검색 결과", f"{int(avg_count):,}")
        with col3:
            high_competition = sum(1 for r in results if r["경쟁도"] == "높음")
            st.metric("높은 경쟁도", f"{high_competition}개")
        
        # 추천 사항
        st.markdown("---")
        st.subheader("💡 추천")
        
        low_competition = [r for r in results if r["경쟁도"] == "낮음"]
        if low_competition:
            st.success("🎯 다음 키워드들은 경쟁이 낮아 진입하기 좋습니다:")
            for item in low_competition:
                st.write(f"- **{item['키워드']}** (검색 결과: {item['검색 결과 수']:,})")
        else:
            st.info("모든 키워드가 높은 경쟁도를 보이고 있습니다. 롱테일 키워드를 고려해보세요.")

def sidebar_info():
    """사이드바 정보"""
    with st.sidebar:
        # 사이드바 로고
        try:
            st.image("../../assets/oryne_logo.png", width="stretch")
            st.markdown("---")
        except:
            st.markdown("### ORYNE")
            st.markdown("---")
        
        st.markdown("### 🎨 테마 설정")
        st.info("""
        💡 **테마 변경 방법:**
        
        상단 우측 메뉴(⋮) → Settings → Theme 에서 변경
        
        - **Light**: 밝은 테마
        - **Dark**: 어두운 테마
        
        다크 모드에서 결과 박스가 더욱 선명하게 보입니다!
        """)
        
        st.markdown("---")
        st.markdown("### ℹ️ 기능 설명")
        st.markdown("""
        **🎯 순위 확인**
        - 특정 쇼핑몰의 상품 순위 확인
        - 최대 10개 키워드 동시 검색
        
        **🔑 연관 키워드**
        - 네이버 광고 API 기반
        - 월간 검색량 정보 제공
        - 상위 50개 연관 키워드 표시
        
        **📊 키워드 분석**
        - 여러 키워드 경쟁도 비교
        - 검색 결과 수 기반 분석
        - 진입 추천 키워드 제안
        """)
        
        st.markdown("---")
        st.markdown("### 🔧 개발 정보")
        st.markdown("""
        - **개발자**: ORYNE
        - **버전**: 2.0.0
        - **기술**: Streamlit, Naver API
        """)

if __name__ == "__main__":
    main()
